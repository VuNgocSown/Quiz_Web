(function($) {
    $(function() {
        var $questionType = $('#id_question_type');
        var $mcqOptions = $('.mcq_options').parent('.form-row');

        function toggleMCQOptions() {
            if ($questionType.val() === 'MCQ') {
                $mcqOptions.show();
            } else {
                $mcqOptions.hide();
            }
        }

        $questionType.on('change', toggleMCQOptions);
        toggleMCQOptions(); // Run once on page load
    });
})(django.jQuery);
