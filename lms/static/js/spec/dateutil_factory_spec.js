define(['../dateutil_factory.js'], function(DateUtilIterator) {
    'use strict';

    describe('DateUtilFactory', function() {
        beforeEach(function() {
            setFixtures('<div class="test"></div>');
        });

        describe('stringHandler', function() {
            it('returns a complete string', function() {
                var localTimeString = 'RANDOM_STRING';
                var sidecarString = 'RANDOM_STRING_TWO';
                var answer = 'RANDOM_STRING_TWO RANDOM_STRING';
                expect(DateUtilIterator.stringHandler(localTimeString, sidecarString)).toEqual(answer);
            });
        });

        describe('transform', function() {
            var $form;

            it('localizes some times', function() {
                /* we have to generate a fake span and then test the resultant texts */
                var iterationKey = '.localized-datetime';
                var TestLangs = {
                    en: 'Due Oct 14, 2016 08:00 UTC',
                    ru: 'Due 14 окт. 2016 г. 08:00 UTC',
                    ar: 'Due ١٤ تشرين الأول أكتوبر ٢٠١٦ ٠٨:٠٠ UTC',
                    fr: 'Due 14 oct. 2016 08:00 UTC'
                };
                $form = $(
                    '<span class="subtitle-name localized-datetime" ' +
                    'data-timezone="UTC" ' +
                    'data-datetime="2016-10-14 08:00:00+00:00" ' +
                    'data-string="Due"></span>'
                );
                Object.keys(TestLangs).forEach(function(key) {
                    $form.attr('lang', String(key));
                    $(document.body).append($form);

                    expect($form.text()).toEqual(TestLangs[key]);

                    $form.remove();
                });
                $form = null;
            });
        });
    });
});
