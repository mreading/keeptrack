// All Javascript for adding a run
$(document).ready(function() {
  show_hide_fields($(".act_type option:selected").text());
})

//---------------------------- Real-time Pace Calculation ----------------------
function set_pace() {
  $("#pace").text(
    function() {
      var seconds = parseInt($("#id_duration_0").val()) * 60 * 60 +
        parseInt($("#id_duration_1").val()) * 60 +
        parseInt($("#id_duration_2").val());
      var distance = $("#id_distance").val();
      if ($("#id_units").val() === "Kilometers") {
        distance = distance * 0.6213
      }
      var seconds_per_mile = seconds / distance;
      var total_seconds = Math.floor(seconds_per_mile % 60).toString();
      var total_minutes = Math.floor(seconds_per_mile / 60).toString();
      if (total_seconds.length === 1) {
        total_seconds = "0".concat(total_seconds)
      }
      $("#pace").text(total_minutes.concat(':',total_seconds, " Min/Mile"));

    }
  )
}

$("#id_distance").change(set_pace);
$("#id_duration_0").change(set_pace);
$("#id_duration_1").change(set_pace);
$("#id_duration_2").change(set_pace);
$("#id_units").change(set_pace);

// -----------------------------------------------------------------------------

// make the duration inputs narrower and side-by-side
$("#id_duration_0").css({"display": "inline-block", "width": "45px"});
$("#id_duration_1").css({"display": "inline-block", "width": "45px"});
$("#id_duration_2").css({"display": "inline-block", "width": "45px"});
$("#id_duration_3").css({"display": "inline-block", "width": "45px"});
$("<p id=pace style='display:inline-block;padding-left:10px;'></p>").insertAfter( "#id_duration_3" );

$(".wu_units").css({"display":"inline-block", "width": "100px"});
$(".cd_units").css({"display":"inline-block", "width": "100px"});
$(".warmup").css({"display":"inline-block", "width": "147px"});
$(".cooldown").css({"display":"inline-block", "width": "147px"});
//-------------------- Show and hide fields depending on the type---------------
function show_hide_fields(act_type){
  $('.control-group').hide();
  $('.act_type').show();
  switch(act_type) {

    case "Interval Run":
      $('.date').show();
      $('.warmup').show();
      $('.wu_units').show();
      $('.cooldown').show();
      $('.cd_units').show();
      $('.comments').show();
      $('.user_label').show();
      $('.shoe').show();
      $('.repeats').show();
      $('.repeats').insertAfter($('.cd_units'));
      break;

    case "Normal Run":
      $('.date').show();
      $('.distance').show();
      $('.units').show();
      $('.duration').show();
      $('.comments').show();
      $('.user_label').show();
      $('.shoe').show();
      break;

    case "Cross Train":
      $('.sport').show();
      $('.date').show();
      $('.distance').show();
      $('.units').show();
      $('.duration').show();
      $('.comments').show();
      $('.user_label').show();
      $('.shoe').show();
      break;

    case "Event":
      $('.date').show();
      $('.warmup').show();
      $('.wu_units').show();
      $('.cooldown').show();
      $('.cd_units').show();
      $('.distance').show();
      $('.units').show();
      $('.duration').show();
      $('.location').show();
      $('.place').show();
      $('.comments').show();
      $('.user_label').show();
      $('.shoe').show();
      break;

    case "-":
      $('.control-group').hide();
      $('.act_type').show();
      break;
  }
}

$(".act_type").change(function() {
  show_hide_fields($(".act_type option:selected").text());
});

// ----------Javascript for dynamic repeats for interval runs.--------------
(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp('(' + prefix + '-\\d+-)|(^)'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find('input,select,textarea,label').length > 0;
            },

            insertDeleteLink = function(row) {
                if (row.is('TR')) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    row.children(':last').append('<a class="' + options.deleteCssClass +'" href="javascript:void(0)">' + options.deleteText + '</a>');
                } else if (row.is('UL') || row.is('OL')) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    row.append('<li><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a></li>');
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    row.append('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText +'</a>');
                }
                row.find('a.' + options.deleteCssClass).click(function() {
                    var row = $(this).parents('.' + options.formCssClass),
                        del = row.find('input:hidden[id $= "-DELETE"]');
                    if (del.length) {
                        // We're dealing with an inline formset; rather than remove
                        // this form from the DOM, we'll mark it as deleted and hide
                        // it, then let Django handle the deleting:
                        del.val('on');
                        row.hide();
                    } else {
                        row.remove();
                        // Update the TOTAL_FORMS form count.
                        // Also update names and IDs for all remaining form controls so they remain in sequence:
                        var forms = $('.' + options.formCssClass).not('.formset-custom-template');
                        $('#id_' + options.prefix + '-TOTAL_FORMS').val(forms.length);
                        for (var i=0, formCount=forms.length; i<formCount; i++) {
                            applyExtraClasses(forms.eq(i), i);
                            forms.eq(i).find('input,select,textarea,label').each(function() {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                del.remove();
            }
            if (hasChildElements(row)) {
                insertDeleteLink(row);
                row.addClass(options.formCssClass);
                applyExtraClasses(row, i);
            }
        });

        if ($$.length) {
            var addButton, template;
            if (options.formTemplate) {
                // If a form template was specified, we'll clone it to generate new form instances:
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass).addClass('formset-custom-template');
                template.find('input,select,textarea,label').each(function() {
                    updateElementIndex($(this), options.prefix, 2012);
                });
                insertDeleteLink(template);
            } else {
                // Otherwise, use the last form in the formset; this works much better if you've got
                // extra (>= 1) forms (thnaks to justhamade for pointing this out):
                template = $('.' + options.formCssClass + ':last').clone(true).removeAttr('id');
                template.find('input:hidden[id $= "-DELETE"]').remove();
                template.find('input,select,textarea,label').each(function() {
                    var elem = $(this);
                    // If this is a checkbox or radiobutton, uncheck it.
                    // This fixes Issue 1, reported by Wilson.Andrew.J:
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.attr('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }
            // FIXME: Perhaps using $.data would be a better idea?
            options.formTemplate = template;

            if ($$.attr('tagName') == 'TR') {
                // If forms are laid out as table rows, insert the
                // "add" button in a new table row:
                var numCols = $$.eq(0).children().length;
                $$.parent().append('<tr><td colspan="' + numCols + '"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></tr>');
                addButton = $$.parent().find('tr:last a');
                addButton.parents('tr').addClass(options.formCssClass + '-add');
            } else {
                // Otherwise, insert it immediately after the last form:
                $$.filter(':last').after('<a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a>');
                addButton = $$.filter(':last').next();
            }
            addButton.click(function() {
                var formCount = parseInt($('#id_' + options.prefix + '-TOTAL_FORMS').val()),
                    row = options.formTemplate.clone(true).removeClass('formset-custom-template'),
                    buttonRow = $(this).parents('tr.' + options.formCssClass + '-add').get(0) || this;
                applyExtraClasses(row, formCount);

                // this is how you get the data before the form has been submitted.
                // console.log(document.intervalform['form-0-rep_distance'].value)
                row.insertBefore($(buttonRow)).show();
                row.find('input,select,textarea,label').each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                $('#id_' + options.prefix + '-TOTAL_FORMS').val(formCount + 1);
                // If a post-add callback was supplied, call it with the added form:

                // When adding a rep, let the initial values be those of the previous rep

                document.forms[0]['form-'+(formCount).toString()+'-rep_distance'].value = document.forms[0]['form-'+(formCount-1)+'-rep_distance'].value;
                document.forms[0]['form-'+(formCount).toString()+'-duration_0'].value = document.forms[0]['form-'+(formCount-1)+'-duration_0'].value;
                document.forms[0]['form-'+(formCount).toString()+'-duration_1'].value = document.forms[0]['form-'+(formCount-1)+'-duration_1'].value;
                document.forms[0]['form-'+(formCount).toString()+'-duration_2'].value = document.forms[0]['form-'+(formCount-1)+'-duration_2'].value;
                document.forms[0]['form-'+(formCount).toString()+'-duration_3'].value = document.forms[0]['form-'+(formCount-1)+'-duration_3'].value;
                document.forms[0]['form-'+(formCount).toString()+'-rep_rest'].value = document.forms[0]['form-'+(formCount-1)+'-rep_rest'].value;
                document.forms[0]['form-'+(formCount).toString()+'-rep_units'].value = document.forms[0]['form-'+(formCount-1)+'-rep_units'].value;

                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    }

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                  // The form prefix for your django formset
        formTemplate: null,              // The jQuery selection cloned to generate new form instances
        addText: 'add another',          // Text for the add link
        deleteText: 'remove',            // Text for the delete link
        addCssClass: 'add-row',          // CSS class applied to the add link
        deleteCssClass: 'delete-row',    // CSS class applied to the delete link
        formCssClass: 'dynamic-form',    // CSS class applied to each form in a formset
        extraClasses: [],                // Additional CSS classes, which will be applied to each form in turn
        added: null,                     // Function called each time a new form is added
        removed: null                    // Function called each time a form is deleted
    };
})(jQuery);

$('.link-formset').formset({
    addText: 'Add Repeat',
    deleteText: 'Remove'
});
