"""
Tests for the functionality and infrastructure of grades tasks.
"""

import ddt
from django.conf import settings
from mock import patch
from unittest import skip

from student.models import anonymous_id_for_user
from student.tests.factories import UserFactory
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory, check_mongo_calls

from lms.djangoapps.grades.config.models import PersistentGradesEnabledFlag
from lms.djangoapps.grades.signals.signals import SCORE_CHANGED
from lms.djangoapps.grades.tasks import recalculate_subsection_grade


@patch.dict(settings.FEATURES, {'PERSISTENT_GRADES_ENABLED_FOR_ALL_TESTS': False})
@ddt.ddt
class RecalculateSubsectionGradeTest(ModuleStoreTestCase):
    """
    Ensures that the recalculate subsection grade task functions as expected when run.
    """
    def setUp(self):
        super(RecalculateSubsectionGradeTest, self).setUp()
        self.user = UserFactory()
        PersistentGradesEnabledFlag.objects.create(enabled_for_all_courses=True, enabled=True)

    def set_up_course(self, enable_subsection_grades=True):
        """
        Configures the course for this test.
        """
        # pylint: disable=attribute-defined-outside-init,no-member
        self.course = CourseFactory.create(
            org='edx',
            name='course',
            run='run',
        )
        if not enable_subsection_grades:
            PersistentGradesEnabledFlag.objects.create(enabled=False)

        self.chapter = ItemFactory.create(parent=self.course, category="chapter", display_name="Chapter")
        self.sequential = ItemFactory.create(parent=self.chapter, category='sequential', display_name="Open Sequential")
        self.problem = ItemFactory.create(parent=self.sequential, category='problem', display_name='problem')

        self.score_changed_kwargs = {
            'points_possible': 10,
            'points_earned': 5,
            'user': self.user.id,
            'course_id': unicode(self.course.id),
            'usage_id': unicode(self.problem.location),
        }

        # this call caches the anonymous id on the user object, saving 4 queries in all happy path tests
        _ = anonymous_id_for_user(self.user, self.course.id)
        # pylint: enable=attribute-defined-outside-init,no-member

    def test_score_changed_signal_queues_task(self):
        """
        Ensures that the SCORE_CHANGED signal enqueues a recalculate subsection grade task.
        """
        self.set_up_course()
        with patch(
            'lms.djangoapps.grades.tasks.recalculate_subsection_grade.apply_async',
            return_value=None
        ) as mock_task_apply:
            # This test checks the signal prep and send, so we need to "undo" the preprocessing done in set_up_course
            initial_kwargs = self.score_changed_kwargs.copy()
            self.score_changed_kwargs.update({'user': self.user})

            SCORE_CHANGED.send(sender=None, **self.score_changed_kwargs)
            mock_task_apply.assert_called_once_with(kwargs=initial_kwargs)

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_subsection_grade_updated(self, default_store):
        with self.store.default_store(default_store):
            self.set_up_course()
            self.assertTrue(PersistentGradesEnabledFlag.feature_enabled(self.course.id))
            with check_mongo_calls(2) and self.assertNumQueries(13):
                recalculate_subsection_grade.apply(kwargs=self.score_changed_kwargs)

    def test_single_call_to_create_block_structure(self):
        self.set_up_course()
        self.assertTrue(PersistentGradesEnabledFlag.feature_enabled(self.course.id))
        with patch(
            'openedx.core.lib.block_structure.factory.BlockStructureFactory.create_from_cache',
            return_value=None,
        ) as mock_block_structure_create:
            recalculate_subsection_grade.apply(kwargs=self.score_changed_kwargs)
            self.assertEquals(mock_block_structure_create.call_count, 1)

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_query_count_does_not_change_with_more_problems(self, default_store):
        with self.store.default_store(default_store):
            self.set_up_course()
            self.assertTrue(PersistentGradesEnabledFlag.feature_enabled(self.course.id))
            ItemFactory.create(parent=self.sequential, category='problem', display_name='problem2')
            ItemFactory.create(parent=self.sequential, category='problem', display_name='problem3')
            with check_mongo_calls(2) and self.assertNumQueries(13):
                recalculate_subsection_grade.apply(kwargs=self.score_changed_kwargs)

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_subsection_grades_not_enabled_on_course(self, default_store):
        with self.store.default_store(default_store):
            self.set_up_course(enable_subsection_grades=False)
            self.assertFalse(PersistentGradesEnabledFlag.feature_enabled(self.course.id))
            with check_mongo_calls(2) and self.assertNumQueries(0):
                recalculate_subsection_grade.apply(kwargs=self.score_changed_kwargs)

    @skip("Pending completion of TNL-5089")
    @ddt.data(
        (ModuleStoreEnum.Type.mongo, True),
        (ModuleStoreEnum.Type.split, True),
        (ModuleStoreEnum.Type.mongo, False),
        (ModuleStoreEnum.Type.split, False),
    )
    @ddt.unpack
    def test_query_counts_with_feature_flag(self, default_store, feature_flag):
        PersistentGradesEnabledFlag.objects.create(enabled=feature_flag)
        with self.store.default_store(default_store):
            self.set_up_course()
            with check_mongo_calls(0) and self.assertNumQueries(3 if feature_flag else 2):
                recalculate_subsection_grade.apply(throw=True, kwargs=self.score_changed_kwargs)

    @ddt.data('user', 'course_id', 'usage_id')
    def test_missing_kwargs(self, kwarg):
        self.set_up_course()
        self.assertTrue(PersistentGradesEnabledFlag.feature_enabled(self.course.id))
        del self.score_changed_kwargs[kwarg]
        with self.assertRaises(KeyError):
            recalculate_subsection_grade.apply(throw=True, kwargs=self.score_changed_kwargs)
