function submit_form() {
  const token = getElementByXPath("//input[@name='token'][1]").value;
  const questions = [];
  const answers = [];
  var elements = document.getElementsByTagName("label");
  for (let i = 0; i < elements.length; i++) {
    questions.push(elements[i].innerHTML);
    name = elements[i].getAttribute("for");
    answers.push(getElementByXPath("//*[@name='"+name+"'][1]").value);
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

function getElementByXPath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

function getElementsByXPath(xpath) {
  const elements = [];
  const xpathResult = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
  let element = xpathResult.iterateNext();
  while (element) {
    elements.push(element);
    element = xpathResult.iterateNext();
  }
  return elements;
}

function radio_hide(question_id, choice_id) {
    elements = getElementsByXPath("//div[@hidden_by='"+question_id.toString()+"' and contains(@hidden_by_choice,';"+choice_id.toString()+";')]");
    if (elements.length > 0) {
        elements.forEach(function(element) {
          inputs = element.querySelectorAll('input');
              inputs.forEach(input => {
                input.checked = false;
                input.required = false;
          });
          element.style.display = "none";
        });
    } else {
        elements = getElementsByXPath("//div[@hidden_by='"+question_id.toString()+"' and not(contains(@hidden_by_choice,';"+choice_id.toString()+";'))]");
        if (elements.length > 0) {
            elements.forEach(function(element) {
                inputs = element.querySelectorAll('input');
                inputs.forEach(input => {
                    if (input.classList.contains("training-required"))
                    {
                      input.required = true;
                    }
                });
                element.style.display = "block";
            });
        }
    }
}
