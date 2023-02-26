function trainingShowHideOldParts (e)
{
    checked = e.checked;
    const major_parts = document.querySelectorAll('.major_part');
    major_parts.forEach(function(major_part) {
        console.log(major_part.id);
    });
}