function trainingShowHideOldParts ()
{
    const checkbox = document.getElementById('training_show_hide_checkbox');
    checked = checkbox.checked;
    const actual_part = document.evaluate("//div[@name='state']/button[@aria-checked='true']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.getAttribute("data-value");
    const major_parts = document.querySelectorAll('.training_major_part');
    major_parts.forEach(function(major_part) {
        const part = document.evaluate("//div[@class='training_major_part' and @id='"+major_part.id+"']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (part != null){
        if (major_part.id != actual_part) {
            if (checked) {
                part.style.display = "block";
            } else {
                part.style.display = "none";
            }
        } else {
            part.style.display = "block";
        }
        }
    });
}