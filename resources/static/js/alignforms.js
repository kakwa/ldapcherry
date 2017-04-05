var classes = ["lcform-col-1", "lcform-col-2"];
var j, len_j = classes.length;
for(j=0; j < len_j; j++){
    var formSelector = classes[j];
    var forms = document.getElementsByClassName(formSelector);
    //console.log(formSelector);
    //console.log(forms);
    if (forms.length > 0){
        forms[0].style.removeProperty("display");
        var InputGroups = forms[0].getElementsByClassName("input-group-addon");
        //console.log(InputGroups);
        var i, len = InputGroups.length;
        var longest = 0;
        for(i=0; i < len; i++){
            if (InputGroups[i].id !== "basic-addon-password2"){
                longest = longest < InputGroups[i].clientWidth ? InputGroups[i].clientWidth : longest;
            }
        }
        for(i=0; i < len; i++){
            InputGroups[i].style.minWidth = (longest + 0) + "px";
        }
        //console.log(longest);
    }
}
//console.log("end_re");
