$(document).ready(function() {

    $('#run').on('click', function() {
        $.ajax({
            url: "/search",
            type: "GET",
            data: { job_title: $("#job_title").val() },
            success: function (data) {
                console.log(data);
                $("#true_job_title_1").val(data.true_job_title[0]);
                $("#true_job_title_2").val(data.true_job_title[1]);
                $("#true_job_title_3").val(data.true_job_title[2]);
            }
        })
    });

    $('body').keypress(function(event) {
        if (event.keyCode == 13) {
            $.ajax({
                url: "/search",
                type: "GET",
                data: { job_title: $("#job_title").val() },
                success: function (data) {
                    console.log(data);
                    $("#true_job_title_1").val(data.true_job_title[0]);
                    $("#true_job_title_2").val(data.true_job_title[1]);
                    $("#true_job_title_3").val(data.true_job_title[2]);
                }
            })
        }
    });

});
