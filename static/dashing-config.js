/* global $, Dashboard */

var dashboard = new Dashboard();

dashboard.addWidget('total_users_widget', 'Number', {
    getData: function () {
        var self = this;
        this.interval = 60000;

        $.extend(this.data, {
            title: "Something",
            more_info: "",
            updated_at: "",
            detail: "",
        });

        $.getJSON('widgets/total_users_widget/render', function (data) {
            console.log(data.value);
            this.data.value = data.value;
        });
    }
});
