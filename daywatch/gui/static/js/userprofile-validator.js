django.jQuery(document).ready(function(){
    django.jQuery('select[name*="_access"]').bind('change', function(data) {
	/*
	 * Just some week limit default values for the different types of accounts in DW
	 */
	var newValue = django.jQuery(this).val();
	var weekLimitElement = django.jQuery('input[id="id_userprofile-0-week_history_limit"]');
	switch (newValue) {
	case "TRIAL":
	    weekLimitElement.fadeOut(400, function(){
		weekLimitElement[0].value = 4;
	    }).fadeIn();
	    break;
	case "LITE":
	    weekLimitElement.fadeOut(400, function(){
		weekLimitElement[0].value = 2;
	    }).fadeIn();
	    break;
	default:
	}
    });
});
