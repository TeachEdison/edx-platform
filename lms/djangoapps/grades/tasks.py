"""
This module contains tasks for asynchronous execution of grade updates.
"""

from celery import task
from django.contrib.auth.models import User

from lms.djangoapps.course_blocks.api import get_course_blocks
from lms.djangoapps.courseware.courses import get_course_by_id
from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.locator import CourseLocator
from openedx.core.djangoapps.content.block_structure.api import get_course_in_cache

from .config.models import PersistentGradesEnabledFlag
from .transformer import GradesTransformer
from .new.subsection_grade import SubsectionGradeFactory


@task()
def recalculate_subsection_grade(**kwargs):  # pylint: disable=unused-argument
    """
    Updates a saved subsection grade.
    This method expects that the kwargs dictionary will contain the following
    entries:
       - user: serialized id of applicable User object
       - course_id: Unicode string representing the course
       - usage_id: Unicode string indicating the courseware instance
    """
    course_key = CourseLocator.from_string(kwargs['course_id'])
    if not PersistentGradesEnabledFlag.feature_enabled(course_key):
        return

    student = User.objects.get(id=kwargs['user'])
    scored_block_usage_key = UsageKey.from_string(kwargs['usage_id']).replace(course_key=course_key)

    collected_block_structure = get_course_in_cache(course_key)
    course = get_course_by_id(course_key, depth=0)
    subsection_grade_factory = SubsectionGradeFactory(student, course, collected_block_structure)
    subsections_to_update = collected_block_structure.get_transformer_block_field(
        scored_block_usage_key,
        GradesTransformer,
        'subsections',
        set()
    )

    for subsection_usage_key in subsections_to_update:
        transformed_subsection_structure = get_course_blocks(
            student,
            subsection_usage_key,
            collected_block_structure=collected_block_structure,
        )
        subsection_grade_factory.update(
            transformed_subsection_structure[subsection_usage_key], transformed_subsection_structure
        )
