classes = ['lcform-col-1', 'lcform-col-2']; 
for(var j in classes){
    var formSelector = classes[j];
    var forms = document.getElementsByClassName(formSelector);
    //console.log(formSelector);
    //console.log(forms);
    if (forms.length > 0){
        var in_groups = forms[0].getElementsByClassName('input-group-addon');
        //console.log(in_groups);
        var i, len = in_groups.length;
        var longest = 0;
        for(i=0; i < len; i++){
            if (in_groups[i].id != 'basic-addon-password2'){
                longest = longest < in_groups[i].clientWidth ? in_groups[i].clientWidth : longest;
            }
        }
        for(i=0; i < len; i++){
            in_groups[i].style.minWidth = (longest + 0) + 'px';
        }
        //console.log(longest);
    }
}
//console.log("end_re");
