$(document).ready(function () {
    $(window).off("resize");
    mdlInitializations();
    enableButtons();
    $(".mdl-layout-title").on("click", function () {
        if (window.location.href.split('/').pop() !== "") {
            window.location.href = '/';
        }
    });
    
    $(window).resize(function() {
    	  //resize just happened, pixels changed
    	var windowWidth = $(window).width();
    	if (windowWidth > 500) {
    		initMap();
    	}
    });
});

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
            break;
        }
    }
}

enableButtons = function () {
    $(".import-list-btn").click(function () {
            document.querySelector('#import-dialog').showModal();
            $('#import_file_field').removeClass("is-focused");
        }
    );

    $('.confirm-import').click(function () {
        document.querySelector('#import-dialog').close();
    });

    $('.close-import-list-dialog').click(function () {
        document.querySelector('#import-dialog').close();
    });
};

mdlInitializations = function () {
    // Polyfill for browsers that don't support the dialog tag.
    var dialogs = document.querySelectorAll('dialog');
    for (var i = 0; i < dialogs.length; i++) {
        // Using an old school style for loop since this for compatibility.
        var dialog = dialogs[i];
        if (!dialog.showModal) {
            dialogPolyfill.registerDialog(dialog);
        }
    }
};




