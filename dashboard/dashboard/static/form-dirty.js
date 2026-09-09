document.addEventListener('change', function (e) {
  const form = e.target.closest('.basics-form');
  if (form) {
    const actions = document.querySelector('.basics-actions');
    if (actions) actions.classList.add('visible');
  }
});

document.addEventListener('htmx:afterSwap', function (e) {
  if (e.target.id === 'basic_information') {
    const actions = document.querySelector('.basics-actions');
    if (actions) actions.classList.remove('visible');
  }
});
