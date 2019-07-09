/* 
 * Licensed under the MIT public license.
 *
 * Part of LdapCherry.
 *
 * Functions to autofill form fields from other fields.
 *
*/

function normalizeName(name) {
    return removeDiacritics(name).toLowerCase().replace(/[^a-z]/g, '');
}

function lcUidExt(firstname, lastname, firstnameEnd, lastnameEnd){
    return normalizeName(firstname).substring(0, parseInt(firstnameEnd))+normalizeName(lastname).substring(0,parseInt(lastnameEnd));
}

function lcUid(firstname, lastname){
    return lcUidExt(firstname, lastname, 0, 7);
}

function lcDisplayName(firstname, lastname){
    return firstname+' '+lastname;
}

function lcMailExt(firstname, lastname, domain, firstnameEnd, lastnameEnd){
    return lcUidExt(firstname, lastname, firstnameEnd, lastnameEnd)+domain;
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
