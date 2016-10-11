
/**
 *
 * A helper function to utilize DateUtils quickly in iterative display templates.
 *
 * @param: {string} data-datetime A pre-localized datetime string, assumed to be in UTC.
 * @param: {string} data-timezone (optional) A user-set timezone preference.
 * @param: {string} lang The user's preferred language.
 * @param: {object} data-format (optional) a format constant as defined in DataUtil.dateFormatEnum.
 *
 * @param: {string} data-string (optional) a string for parsing through StringUtils after localizing
 * datetime
 *
 * @return: {string} a user-time, localized, formatted datetime string
 *
 */

(function(define) {
    'use strict';

    define([
        'jquery',
        'edx-ui-toolkit/js/utils/date-utils',
        'edx-ui-toolkit/js/utils/string-utils'
    ], function($, DateUtils, StringUtils) {
    //     return function() {
        var DateUtilIterator;
        var localizedTime;
        var stringHandler;
        var displayDatetime;
        var isValid;
        var transform;

        transform = function(iterationKey) {
            var context;

            $(iterationKey).each(function() {
                if (isValid($(this).data('datetime'))) {
                    context = {
                        datetime: $(this).data('datetime'),
                        timezone: $(this).data('timezone'),
                        language: $(this).attr('lang'),
                        format: $(this).data('format')
                    };
                    displayDatetime = stringHandler(
                        localizedTime(context),
                        $(this).data('string')
                    );
                    /*
                    to show the prototype in action, check the console
                    */
                    /* eslint-disable no-alert, no-console */
                    console.log(displayDatetime);
                    /* eslint-enable no-alert, no-console */

                    /*
                    uncomment the following line once approved
                    */
                    // $(this).text(displayDatetime);
                    // return displayDatetime;
                }
            });

            // COMMENT THIS OUT ONCE FEATURE IS READY
            return displayDatetime;
        };

        localizedTime = function(context) {
            return DateUtils.localize(context);
        };

        stringHandler = function(localTimeString, sidecarString) {
            var returnString;
            if (isValid(sidecarString)) {
                returnString = StringUtils.interpolate(
                    '{string} {date}',
                    {
                        string: sidecarString,
                        date: localTimeString
                    }
                );
            } else {
                returnString = localTimeString;
            }
            return returnString;
        };

        isValid = function(candidateVariable) {
            return candidateVariable !== undefined
                && candidateVariable !== ''
                && candidateVariable !== 'Invalid date'
                && candidateVariable !== 'None';
        };
        DateUtilIterator = {
            transform: transform,
            stringHandler: stringHandler,
            displayDatetime: displayDatetime
        };
        return DateUtilIterator;
    });
}).call(this, define || RequireJS.define);

