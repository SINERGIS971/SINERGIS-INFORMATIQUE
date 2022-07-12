element = document.evaluate("//div[@role='menuitemcheckbox' and @aria-label='SINERGIS MQE']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
if (element.firstChild.firstChild.classList.contains("fa-square-o"))
{
  element.click();
}
