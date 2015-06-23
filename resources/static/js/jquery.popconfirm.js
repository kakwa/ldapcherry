/*!
 * PopConfirm 0.4.3
 * http://ifnot.github.io/PopConfirm/
 *
 * Use jQuery & Bootstrap
 * http://jquery.com/
 * http://getbootstrap.com/
 *
 * Copyright 2014 Anael Favre and other contributors
 * Released under the MIT license
 * https://raw.github.com/AnaelFavre/PopConfirm/master/LICENCE
 *
 * Thanks to contributors :
 * Thomas Hanson https://github.com/diresquirrel
 * Mohamed Aymen https://github.com/kernel64
 * Muhammad Ubaid Raza https://github.com/mubaidr
 */

(function ($) {
  'use strict';
  /*global jQuery, $*/
  /*jslint nomen: true, evil: true*/
  $.fn.extend({
    popConfirm: function (options) {
      var defaults = {
          title: 'Confirmation',
          content: 'Are you really sure ?',
          placement: 'right',
          container: 'body',
          yesBtn: 'Yes',
          noBtn: 'No'
        },
        last = null;
      options = $.extend(defaults, options);
      return this.each(function () {
        var self = $(this),
          arrayActions = [],
          arrayDelegatedActions = [],
          eventToConfirm,
          optName,
          optValue,
          i,
          elmType,
          code,
          form;

        // Load data-* attriutes
        for (optName in options) {
          if (options.hasOwnProperty(optName)) {
            optValue = $(this).attr('data-confirm-' + optName);
            if (optValue) {
              options[optName] = optValue;
            }
          }
        }

        // If there are jquery click events
        if (jQuery._data(this, "events") && jQuery._data(this, "events").click) {

          // Save all click handlers
          for (i = 0; i < jQuery._data(this, "events").click.length; i = i + 1) {
            arrayActions.push(jQuery._data(this, "events").click[i].handler);
          }

          // unbind it to prevent it firing
          $(self).unbind("click");
        }

        // If there are jquery delegated click events
        if (self.data('remote') && jQuery._data(document, "events") && jQuery._data(document, "events").click) {

          // Save all delegated click handlers that apply
          for (i = 0; i < jQuery._data(document, "events").click.length; i = i + 1) {
            elmType = self[0].tagName.toLowerCase();
            if (jQuery._data(document, "events").click[i].selector && jQuery._data(document, "events").click[i].selector.indexOf(elmType + "[data-remote]") !== -1) {
              arrayDelegatedActions.push(jQuery._data(document, "events").click[i].handler);
            }
          }
        }

        // If there are hard onclick attribute
        if (self.attr('onclick')) {
          // Extracting the onclick code to evaluate and bring it into a closure
          code = self.attr('onclick');
          arrayActions.push(function () {
            eval(code);
          });
          $(self).prop("onclick", null);
        }

        // If there are href link defined
        if (!self.data('remote') && self.attr('href')) {
          // Assume there is a href attribute to redirect to
          arrayActions.push(function () {
            window.location.href = self.attr('href');
          });
        }

        // If the button is a submit one
        if (self.attr('type') && self.attr('type') === 'submit') {
          // Get the form related to this button then store submiting in closure
          form = $(this).parents('form:first');
          arrayActions.push(function () {
            form.submit();
          });
        }

        self.popover({
          trigger: 'manual',
          title: options.title,
          html: true,
          placement: options.placement,
          container: options.container,
          //Avoid using multiline strings, nno support in older browsers.
          content: options.content + '<p class="button-group" style="margin-top: 10px; text-align: center;"><button type="button" class="btn btn-small confirm-dialog-btn-abord">' + options.noBtn + '</button> <button type="button" class="btn btn-small btn-danger confirm-dialog-btn-confirm">' + options.yesBtn + '</button></p>'
        }).click(function (e) {
          if (last && last !== self) {
            last.popover('hide').removeClass('popconfirm-active');
          }
          last = self;
        });

        $(document).on('click', function () {
          if (last) {
            last.popover('hide').removeClass('popconfirm-active');
          }
        });

        self.bind('click', function (e) {
          eventToConfirm = e;

          e.preventDefault();
          e.stopPropagation();

          $('.popconfirm-active').not(self).popover('hide').removeClass('popconfirm-active');
          self.popover('show').addClass('popconfirm-active');

          $(document).find('.popover .confirm-dialog-btn-confirm').bind('click', function (e) {
            for (i = 0; i < arrayActions.length; i = i + 1) {
              arrayActions[i].apply(self);
            }

            for (i = 0; i < arrayDelegatedActions.length; i = i + 1) {
              arrayDelegatedActions[i].apply(self, [eventToConfirm.originalEvent]);
            }

            self.popover('hide').removeClass('popconfirm-active');
          });
          $(document).find('.popover .confirm-dialog-btn-abord').bind('click', function (e) {
            self.popover('hide').removeClass('popconfirm-active');
          });
        });
      });
    }
  });
}(jQuery));
