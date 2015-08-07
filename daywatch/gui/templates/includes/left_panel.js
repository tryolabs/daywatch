{% load i18n %}

var country_sites = {{country_sites | safe}};

function filter_companies() {
    var selected_country = $('#id_country').val();
    var sites = country_sites[selected_country];
    $('.companies label').each(function(idx, label) {
        var input = $(label).find('input');
        var company_id = parseInt(input.val());
        if($.inArray(company_id, sites) > -1) {
            $(label).show();
            input.prop('disabled', false);
        } else {
            $(label).hide();
            input.prop('disabled', true);
        }
    });
}

$(document).ready(function() {
    // Set the tooltips
    $('*[data-toggle=tooltip]').tooltip({'placement': 'top'});
    $('#id_country').tooltip({'title':'{% blocktrans %}Country to monitor.{% endblocktrans %}'});
    $('#id_result_type').tooltip({'title':'{% blocktrans %}Type of result.{% endblocktrans %}'});
    $('#id_period').tooltip({'title':'{% blocktrans %}Period to monitor. You can select a predetermined or custom range.{% endblocktrans %}'});
    $('#refresh').tooltip({'title':"{% blocktrans %}Click to update the data.{% endblocktrans %}"});

    // Set the datepicker
    $.fn.datepicker.defaults.format = "yyyy/mm/dd";

    $("#id_start_date").datepicker('setDate', new Date());
    $("#id_end_date").datepicker('setDate', new Date());
    $("#dates_div :input").prop('disabled', true);
    $("#dates_div").hide();
    $('#id_period :first-child').prop('selected', true);

    $('#id_period').change(function() {
        // slideUp and Down don't work, probably because of positioning issues
        if ($('#id_period').val() == 'custom'){
            $('#dates_div').slideDown();
            $("#dates_div :input").prop('disabled', false);
        } else {
            $('#dates_div').slideUp();
            $("#dates_div :input").prop('disabled', true);
        }
    });

    // When the 'All companies/categories' button is checked, all of those are
    // checked
    $('#id_all_companies').click(function() {
        var checkboxes = $('fieldset.companies input[type=checkbox]');
        checkboxes.prop('checked',checkboxes.prop('checked'));
    });

    $('#id_all_categories').click(function() {
        var checkboxes = $('fieldset.categories input[type=checkbox]');
        checkboxes.prop('checked',checkboxes.prop('checked'));
    });

    // Initial state of the checkboxes
    $("#categories_div :input").prop('checked', true);
    $("#id_all_categories").prop('checked', true);

    // When one of the checkboxes is unchecked, the corresponding 'all
    // categories/companies' checkbox is unchecked
    $("#categories_div :input").change(function() {
        $('#id_all_categories').prop('checked', false);
    });

    $("#companies_div :input").change(function() {
        $('#id_all_companies').prop('checked', false);
    });

    $('#id_country').change(filter_companies);
    $('#id_result_type').change(filter_companies);

    filter_companies();

    $("#refresh").click(function() {
        drawList(action_url);
    });
    $('#left_panel_result_type_div').hide();

    /* Select the tab in the navbar */
    $("#menu_" + nav).addClass("selected");
});

function drawList(url) {
    $.get(url, data = $("#panel-form").serialize())
        .done(function(data) {
            $("#results").empty();
            $('#results').html(data);
            renderAll();
            $('.pagination a').each(function(node) {
                $(this).click(function() {
                    event.preventDefault();
                    paginate(parseInt($(this).text()));
                });
            });
        });
}

function paginate(page_number) {
    drawList(action_url + '?page=' + page_number);
}
