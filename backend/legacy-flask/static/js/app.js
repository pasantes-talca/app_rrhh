document.addEventListener('DOMContentLoaded', function () {
  var root = document.documentElement;
  var themeButtons = document.querySelectorAll('[data-theme-toggle]');

  function renderTheme(theme) {
    root.dataset.theme = theme;
    themeButtons.forEach(function (button) {
      var dark = theme === 'dark';
      var icon = button.querySelector('i');
      var label = button.querySelector('span');
      icon.className = dark ? 'bi bi-sun' : 'bi bi-moon-stars';
      if (label) label.textContent = dark ? 'Modo claro' : 'Modo oscuro';
      button.setAttribute('aria-label', dark ? 'Activar modo claro' : 'Activar modo oscuro');
      button.title = dark ? 'Activar modo claro' : 'Activar modo oscuro';
    });
  }

  renderTheme(root.dataset.theme || 'light');
  themeButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('talca-theme', next);
      renderTheme(next);
    });
  });

  var selector = [
    'select[name*="empleado"]',
    'select[id*="empleado"]',
    'select[name*="supervisor"]',
    'select[id*="supervisor"]'
  ].join(',');

  document.querySelectorAll(selector).forEach(function (select) {
    if (select.dataset.searchReady === 'true') return;
    select.dataset.searchReady = 'true';

    var options = Array.from(select.options).map(function (option) {
      return { value: option.value, text: option.text, disabled: option.disabled };
    });
    var selectedValue = select.value;
    var search = document.createElement('input');
    var isSupervisor = (select.name + ' ' + select.id).toLowerCase().includes('supervisor');
    search.type = 'search';
    search.className = 'form-control employee-select-search';
    search.placeholder = isSupervisor ? 'Escribí para buscar un supervisor' : 'Escribí para buscar un empleado';
    search.autocomplete = 'off';
    search.setAttribute('aria-label', search.placeholder);
    select.parentNode.insertBefore(search, select);

    function normalize(value) {
      return value.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    search.addEventListener('input', function () {
      var term = normalize(search.value.trim());
      var currentValue = select.value || selectedValue;
      var matches = options.filter(function (option, index) {
        return index === 0 || option.value === currentValue || !term || normalize(option.text).includes(term);
      });

      select.replaceChildren();
      matches.forEach(function (item) {
        var option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.text;
        option.disabled = item.disabled;
        option.selected = item.value === currentValue;
        select.appendChild(option);
      });

      if (term && matches.length === 1) {
        var empty = document.createElement('option');
        empty.textContent = 'No se encontraron coincidencias';
        empty.disabled = true;
        select.appendChild(empty);
      }
    });

    select.addEventListener('change', function () {
      selectedValue = select.value;
    });
  });
});
