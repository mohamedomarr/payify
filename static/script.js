// Example starter JavaScript for disabling form submissions if there are invalid fields
(function() {
    'use strict';
    window.addEventListener('load', function() {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation');
        // Loop over them and prevent submission
        var validation = Array.prototype.filter.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();

// for add links to tables
const newLocal = jQuery(document).ready(function ($) {
    $(".clickable-row").click(function () {
        window.location = $(this).data("href") + $(this).data("name");
    });
});

// modal content in transfer.html
var content = function() {
    // inputed mail
    to_mail = document.getElementById('send_to_mail').value
    document.getElementById('modal_mail').innerHTML = to_mail;
    // inputed amount of money
    to_amount = document.getElementById('send_to_amount').value
    document.getElementById('modal_amount').innerHTML = to_amount;
}

// validtion for password match
var check = function() {
    // if passwords are match print matching
    if (document.getElementById('password').value.length >= 1) {
        if (document.getElementById('password').value ==
        document.getElementById('confrim_password').value) {
        document.getElementById('message').style.color = '#28a745';
        document.getElementById('message').innerHTML = 'matching';
        // if passwords are not match print not matching
        } else {
            document.getElementById('message').style.color = '#dc3545';
            document.getElementById('message').innerHTML = 'not matching';
        } 
    }
}