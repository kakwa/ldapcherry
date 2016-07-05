/* 
 * Licensed under the MIT public license.
 *
 * Part of LdapCherry.
 *
 * Functions to autofill form fields from other fields.
 *
*/

function lcUid(firstname, lastname){
    var ascii_firstname = removeDiacritics(firstname).toLowerCase().replace(/[^a-z]/g, '');
    var ascii_lastname = removeDiacritics(lastname).toLowerCase().replace(/[^a-z]/g, '');
    return ascii_firstname.charAt(0)+ascii_lastname.substring(0,7);
}

function lcDisplayName(firstname, lastname){
    return firstname+' '+lastname;
}

function lcMail(firstname, lastname, domain){
    return lcUid(firstname, lastname)+domain;
}

function lcUidNumber(firstname, lastname, minuid, maxuid){
    var iminuid = parseInt(minuid);
    var imaxuid = parseInt(maxuid);
    return (parseInt('0x'+sha1(firstname+lastname)) % (imaxuid - iminuid)) + iminuid;
}

function lcHomeDir(firstname, lastname, basedir){
    return basedir+lcUid(firstname, lastname);
}
