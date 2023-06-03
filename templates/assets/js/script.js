const exampleDomain = document.getElementById("example-domain");
exampleDomain.innerHTML = window.location.hostname;

const inputField = document.getElementById("try-it-input");
const outputImage = document.getElementById("try-it-output");
const performance = document.getElementById("try-it-performance");

// Add input event listener
inputField.addEventListener("input", function () {
  const startTime = new Date().getTime();
  const inputValue = inputField.value;
  outputImage.src = `${window.location.origin}/generate?data=${inputValue}&size=50`;

  outputImage.onload = function () {
    const endTime = new Date().getTime();
    const responseTime = endTime - startTime;
    performance.innerHTML = responseTime + "ms";
  };

  outputImage.onerror = function () {
    console.error("Error loading identicon");
  };
});
