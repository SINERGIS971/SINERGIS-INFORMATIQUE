function submit_form() {
  const token = getElementByXpath("//input[@name='token'][1]").value;
  const questions = [];
  const answers = [];
  var elements = document.getElementsByTagName("label");
  for (let i = 0; i < elements.length; i++) {
    questions.push(elements[i].innerHTML);
    name = elements[i].getAttribute("for");
    answers.push(getElementByXpath("//*[@name='"+name+"'][1]").value);
  }
  //POST Request
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:8069/training/training", true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
      token : token,
      questions : questions,
      answers : answers
  }));
}

function getElementByXpath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}
