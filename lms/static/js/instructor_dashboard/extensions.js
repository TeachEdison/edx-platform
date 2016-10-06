(function() {
  var Extensions, plantTimeout, std_ajax_err;

  plantTimeout = function() {
    return window.InstructorDashboard.util.plantTimeout.apply(this, arguments);
  };

  std_ajax_err = function() {
    return window.InstructorDashboard.util.std_ajax_err.apply(this, arguments);
  };

  Extensions = (function() {

    function Extensions($section) {
      var $grid_display,
        _this = this;
      this.$section = $section;
      this.$section.data('wrapper', this);
      this.$change_due_date = this.$section.find("input[name='change-due-date']");
      this.$reset_due_date = this.$section.find("input[name='reset-due-date']");
      this.$show_unit_extensions = this.$section.find("input[name='show-unit-extensions']");
      this.$show_student_extensions = this.$section.find("input[name='show-student-extensions']");
      this.$section.find(".request-response").hide();
      this.$section.find(".request-response-error").hide();
      $grid_display = this.$section.find('.data-display');
      this.$grid_text = $grid_display.find('.data-display-text');
      this.$grid_table = $grid_display.find('.data-display-table');
      this.$change_due_date.click(function() {
        var send_data;
        _this.clear_display();
        _this.$student_input = _this.$section.find("#set-extension input[name='student']");
        _this.$url_input = _this.$section.find("#set-extension select[name='url']");
        _this.$due_datetime_input = _this.$section.find("#set-extension input[name='due_datetime']");
        send_data = {
          student: _this.$student_input.val(),
          url: _this.$url_input.val(),
          due_datetime: _this.$due_datetime_input.val()
        };
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: _this.$change_due_date.data('endpoint'),
          data: send_data,
          success: function(data) {
            return _this.display_response("set-extension", data);
          },
          error: function(xhr) {
            return _this.fail_with_error("set-extension", "Error changing due date", xhr);
          }
        });
      });
      this.$reset_due_date.click(function() {
        var send_data;
        _this.clear_display();
        _this.$student_input = _this.$section.find("#reset-extension input[name='student']");
        _this.$url_input = _this.$section.find("#reset-extension select[name='url']");
        send_data = {
          student: _this.$student_input.val(),
          url: _this.$url_input.val()
        };
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: _this.$reset_due_date.data('endpoint'),
          data: send_data,
          success: function(data) {
            return _this.display_response("reset-extension", data);
          },
          error: function(xhr) {
            return _this.fail_with_error("reset-extension", "Error reseting due date", xhr);
          }
        });
      });
      this.$show_unit_extensions.click(function() {
        var send_data, url;
        _this.clear_display();
        _this.$grid_table.text('Loading');
        _this.$url_input = _this.$section.find("#view-granted-extensions select[name='url']");
        url = _this.$show_unit_extensions.data('endpoint');
        send_data = {
          url: _this.$url_input.val()
        };
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: url,
          data: send_data,
          error: function(xhr) {
            return _this.fail_with_error("view-granted-extensions", "Error getting due dates", xhr);
          },
          success: function(data) {
            return _this.display_grid(data);
          }
        });
      });
      this.$show_student_extensions.click(function() {
        var send_data, url;
        _this.clear_display();
        _this.$grid_table.text('Loading');
        url = _this.$show_student_extensions.data('endpoint');
        _this.$student_input = _this.$section.find("#view-granted-extensions input[name='student']");
        send_data = {
          student: _this.$student_input.val()
        };
        return $.ajax({
          type: 'POST',
          dataType: 'json',
          url: url,
          data: send_data,
          error: function(xhr) {
            return _this.fail_with_error("view-granted-extensions", "Error getting due dates", xhr);
          },
          success: function(data) {
            return _this.display_grid(data);
          }
        });
      });
    }

    Extensions.prototype.onClickTitle = function() {};

    Extensions.prototype.fail_with_error = function(id, msg, xhr) {
      var $task_error, $task_response, data;
      $task_error = this.$section.find("#" + id + " .request-response-error");
      $task_response = this.$section.find("#" + id + " .request-response");
      this.clear_display();
      data = $.parseJSON(xhr.responseText);
      msg += ": " + data['error'];
      console.warn(msg);
      $task_response.empty();
      $task_error.empty();
      $task_error.text(msg);
      return $task_error.show();
    };

    Extensions.prototype.display_response = function(id, data) {
      var $task_error, $task_response;
      $task_error = this.$section.find("#" + id + " .request-response-error");
      $task_response = this.$section.find("#" + id + " .request-response");
      $task_error.empty().hide();
      $task_response.empty().text(data);
      return $task_response.show();
    };

    Extensions.prototype.display_grid = function(data) {
      var $table_placeholder, col, columns, grid, grid_data, options;
      this.clear_display();
      this.$grid_text.text(data.title);
      options = {
        enableCellNavigation: true,
        enableColumnReorder: false,
        forceFitColumns: true
      };
      columns = (function() {
        var _i, _len, _ref, _results;
        _ref = data.header;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          col = _ref[_i];
          _results.push({
            id: col,
            field: col,
            name: col
          });
        }
        return _results;
      })();
      grid_data = data.data;
      $table_placeholder = $('<div/>', {
        "class": 'slickgrid',
        style: 'min-height: 400px'
      });
      this.$grid_table.append($table_placeholder);
      return grid = new Slick.Grid($table_placeholder, grid_data, columns, options);
    };

    Extensions.prototype.clear_display = function() {
      this.$grid_text.empty();
      this.$grid_table.empty();
      this.$section.find(".request-response-error").empty().hide();
      return this.$section.find(".request-response").empty().hide();
    };

    return Extensions;

  })();

  if (typeof _ !== "undefined" && _ !== null) {
    _.defaults(window, {
      InstructorDashboard: {}
    });
    _.defaults(window.InstructorDashboard, {
      sections: {}
    });
    _.defaults(window.InstructorDashboard.sections, {
      Extensions: Extensions
    });
  }

}).call(this);
