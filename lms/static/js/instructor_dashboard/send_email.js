(function() {
  var Email, KeywordValidator, PendingInstructorTasks, create_email_content_table, create_email_message_views, create_task_list_table, plantTimeout, std_ajax_err;

  plantTimeout = function() {
    return window.InstructorDashboard.util.plantTimeout.apply(this, arguments);
  };

  std_ajax_err = function() {
    return window.InstructorDashboard.util.std_ajax_err.apply(this, arguments);
  };

  PendingInstructorTasks = function() {
    return window.InstructorDashboard.util.PendingInstructorTasks;
  };

  create_task_list_table = function() {
    return window.InstructorDashboard.util.create_task_list_table.apply(this, arguments);
  };

  create_email_content_table = function() {
    return window.InstructorDashboard.util.create_email_content_table.apply(this, arguments);
  };

  create_email_message_views = function() {
    return window.InstructorDashboard.util.create_email_message_views.apply(this, arguments);
  };

  KeywordValidator = function() {
    return window.InstructorDashboard.util.KeywordValidator;
  };

  this.SendEmail = (function() {

    function SendEmail($container) {
      var _this = this;
      this.$container = $container;
      this.$emailEditor = XBlock.initializeBlock($('.xblock-studio_view'));
      this.$send_to = this.$container.find("input[name='send_to']");
      this.$cohort_targets = this.$send_to.filter('[value^="cohort:"]');
      this.$subject = this.$container.find("input[name='subject']");
      this.$btn_send = this.$container.find("input[name='send']");
      this.$task_response = this.$container.find(".request-response");
      this.$request_response_error = this.$container.find(".request-response-error");
      this.$content_request_response_error = this.$container.find(".content-request-response-error");
      this.$history_request_response_error = this.$container.find(".history-request-response-error");
      this.$btn_task_history_email = this.$container.find("input[name='task-history-email']");
      this.$btn_task_history_email_content = this.$container.find("input[name='task-history-email-content']");
      this.$table_task_history_email = this.$container.find(".task-history-email-table");
      this.$table_email_content_history = this.$container.find(".content-history-email-table");
      this.$email_content_table_inner = this.$container.find(".content-history-table-inner");
      this.$email_messages_wrapper = this.$container.find(".email-messages-wrapper");
      this.$btn_send.click(function() {
        var body, confirm_message, display_target, full_confirm_message, message, send_data, subject, success_message, target, targets, validation, _i, _len;
        subject = _this.$subject.val();
        body = _this.$emailEditor.save()['data'];
        targets = [];
        _this.$send_to.filter(':checked').each(function() {
          return targets.push(this.value);
        });
        if (subject === "") {
          return alert(gettext("Your message must have a subject."));
        } else if (body === "") {
          return alert(gettext("Your message cannot be blank."));
        } else if (targets.length === 0) {
          return alert(gettext("Your message must have at least one target."));
        } else {
          validation = KeywordValidator().validate_string(body);
          if (!validation.is_valid) {
            message = gettext("There are invalid keywords in your email. Check the following keywords and try again.");
            message += "\n" + validation.invalid_keywords.join('\n');
            alert(message);
            return;
          }
          display_target = function(value) {
            if (value === "myself") {
              return gettext("Yourself");
            } else if (value === "staff") {
              return gettext("Everyone who has staff privileges in this course");
            } else if (value === "learners") {
              return gettext("All learners who are enrolled in this course");
            } else {
              return gettext("All learners in the {cohort_name} cohort").replace('{cohort_name}', value.slice(value.indexOf(':') + 1));
            }
          };
          success_message = gettext("Your email message was successfully queued for sending. In courses with a large number of learners, email messages to learners might take up to an hour to be sent.");
          confirm_message = gettext("You are sending an email message with the subject {subject} to the following recipients.");
          for (_i = 0, _len = targets.length; _i < _len; _i++) {
            target = targets[_i];
            confirm_message += "\n-" + display_target(target);
          }
          confirm_message += "\n\n" + gettext("Is this OK?");
          full_confirm_message = confirm_message.replace('{subject}', subject);
          if (confirm(full_confirm_message)) {
            send_data = {
              action: 'send',
              send_to: JSON.stringify(targets),
              subject: subject,
              message: body
            };
            return $.ajax({
              type: 'POST',
              dataType: 'json',
              url: _this.$btn_send.data('endpoint'),
              data: send_data,
              success: function(data) {
                return _this.display_response(success_message);
              },
              error: std_ajax_err(function() {
                return _this.fail_with_error(gettext('Error sending email.'));
              })
            });
          } else {
            _this.task_response.empty();
            return _this.$request_response_error.empty();
          }
        }
      });
      this.$btn_task_history_email.click(function() {
        var url;
        url = _this.$btn_task_history_email.data('endpoint');
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: url,
          success: function(data) {
            if (data.tasks.length) {
              return create_task_list_table(_this.$table_task_history_email, data.tasks);
            } else {
              _this.$history_request_response_error.text(gettext("There is no email history for this course."));
              return _this.$history_request_response_error.css({
                "display": "block"
              });
            }
          },
          error: std_ajax_err(function() {
            return _this.$history_request_response_error.text(gettext("There was an error obtaining email task history for this course."));
          })
        });
      });
      this.$btn_task_history_email_content.click(function() {
        var url;
        url = _this.$btn_task_history_email_content.data('endpoint');
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: url,
          success: function(data) {
            if (data.emails.length) {
              create_email_content_table(_this.$table_email_content_history, _this.$email_content_table_inner, data.emails);
              return create_email_message_views(_this.$email_messages_wrapper, data.emails);
            } else {
              _this.$content_request_response_error.text(gettext("There is no email history for this course."));
              return _this.$content_request_response_error.css({
                "display": "block"
              });
            }
          },
          error: std_ajax_err(function() {
            return _this.$content_request_response_error.text(gettext("There was an error obtaining email content history for this course."));
          })
        });
      });
      this.$send_to.change(function() {
        var targets;
        if ($('input#target_learners:checked').length) {
          _this.$cohort_targets.each(function() {
            this.checked = false;
            this.disabled = true;
            return true;
          });
        } else {
          _this.$cohort_targets.each(function() {
            this.disabled = false;
            return true;
          });
        }
        targets = [];
        $('input[name="send_to"]:checked+label').each(function() {
          return targets.push(this.innerText.replace(/\s*\n.*/g, ''));
        });
        return $(".send_to_list").text(gettext("Send to:") + " " + targets.join(", "));
      });
    }

    SendEmail.prototype.fail_with_error = function(msg) {
      console.warn(msg);
      this.$task_response.empty();
      this.$request_response_error.empty();
      this.$request_response_error.text(msg);
      return $(".msg-confirm").css({
        "display": "none"
      });
    };

    SendEmail.prototype.display_response = function(data_from_server) {
      this.$task_response.empty();
      this.$request_response_error.empty();
      this.$task_response.text(data_from_server);
      return $(".msg-confirm").css({
        "display": "block"
      });
    };

    return SendEmail;

  })();

  Email = (function() {

    function Email($section) {
      var _this = this;
      this.$section = $section;
      this.$section.data('wrapper', this);
      plantTimeout(0, function() {
        return new SendEmail(_this.$section.find('.send-email'));
      });
      this.instructor_tasks = new (PendingInstructorTasks())(this.$section);
    }

    Email.prototype.onClickTitle = function() {
      return this.instructor_tasks.task_poller.start();
    };

    Email.prototype.onExit = function() {
      return this.instructor_tasks.task_poller.stop();
    };

    return Email;

  })();

  _.defaults(window, {
    InstructorDashboard: {}
  });

  _.defaults(window.InstructorDashboard, {
    sections: {}
  });

  _.defaults(window.InstructorDashboard.sections, {
    Email: Email
  });

}).call(this);
