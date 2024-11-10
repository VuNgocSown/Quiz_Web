function toggleMCQOptions(value) {
    var mcqFields = ['option_1', 'option_2', 'option_3', 'option_4', 'correct_answer'];
    mcqFields.forEach(function(field) {
        var fieldDiv = document.querySelector('.field-' + field);
        if (fieldDiv) {
            fieldDiv.style.display = value === 'MCQ' ? 'block' : 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var questionTypeSelect = document.getElementById('id_question_type');
    if (questionTypeSelect) {
        toggleMCQOptions(questionTypeSelect.value);
        questionTypeSelect.addEventListener('change', function() {
            toggleMCQOptions(this.value);
        });
    }
});
