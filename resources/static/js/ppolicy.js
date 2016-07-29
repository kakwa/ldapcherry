$('#form').validator({
    custom: {
        'ppolicy': function($el) {
            if(! $el.prop('required') && $el.val() == 0){
                return true;
            };
            var $ret = 'PPolicy error';
            $.ajax({
                url: '/checkppolicy',
                type: 'POST',
                dataType: 'json',
                async: false,
                data: 'pwd=' + encodeURIComponent($el.val()),
                success: function(data) {
                    $ret = data;
                },
                error: function(jqXHR, exception) {
                    switch (jqXHR.status) {
                        case 400:
                            $ret = {"reason":"Javascript ppolicy.js error","match":false};
                            break;
                        case 403:
                            $ret = {"reason":"Session expired, you must reconnect","match":false};
                            break;
                        case 500:
                            $ret = {"reason":"Server error","match":false};
                            break;
                        default:
                            $ret = {"reason":"Unknown error [" + jqXHR.status + "], check logs","match":false};
                    }
                }
            });
            this.options.errors['ppolicy'] = $ret['reason'];
            return $ret['match'];
        }
    },
    errors: {
        'ppolicy': 'PPolicy error',
    }
})

// vim:set expandtab tabstop=4 shiftwidth=4:
