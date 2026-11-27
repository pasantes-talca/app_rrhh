/* WebAuthn nativo: no envía información biométrica al servidor. */
(() => {
  const root = document.getElementById('receipt-passkey');
  if (!root) return;
  const status = document.getElementById('receipt-passkey-status');
  let registered = root.dataset.registered === 'true';
  const buttons = [...root.querySelectorAll('button')];
  const decode = (value) => {
    const raw = atob(value.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - value.length % 4) % 4));
    return Uint8Array.from(raw, (char) => char.charCodeAt(0));
  };
  const encode = (value) => btoa(String.fromCharCode(...new Uint8Array(value)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
  const post = async (url, body) => {
    const response = await fetch(url, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.getElementById('receipt-csrf').value },
      body: JSON.stringify(body),
    });
    if (!response.ok || response.redirected) {
      const messages = { 400: 'La verificación venció o fue rechazada. Intentá de nuevo.',
        403: 'No se autorizó la operación. Revisá la contraseña y la sesión.',
        409: 'El recibo o el dispositivo cambió. Recargá la página.',
        429: 'Demasiados intentos. Esperá unos minutos.',
        503: 'La firma todavía no está configurada. Contactá a Sistemas.' };
      throw new Error(messages[response.status] || 'No se pudo completar la operación.');
    }
    return response.json();
  };
  const supported = window.isSecureContext && !!window.PublicKeyCredential && !!navigator.credentials;
  if (!supported) {
    status.textContent = 'Necesitás HTTPS y un navegador con passkeys. En pruebas usá localhost.';
    buttons.forEach((button) => { button.disabled = true; });
    return;
  }
  async function ceremony(purpose, answer) {
    const observation = document.getElementById('observacion').value.trim();
    if (purpose === 'sign' && answer === 'Disconforme' && !observation) {
      status.textContent = 'Indicá el motivo de la disconformidad.';
      return;
    }
    if (purpose === 'sign' && !window.confirm(`¿Querés firmar este recibo como ${answer.toLowerCase()}?`)) return;
    buttons.forEach((button) => { button.disabled = true; });
    status.textContent = 'Seguí las instrucciones de tu dispositivo…';
    const passwordInput = document.getElementById('receipt-password');
    try {
      const input = purpose === 'register'
        ? { purpose, password: passwordInput.value }
        : { purpose, respuesta: answer, observacion: observation };
      const result = await post(root.dataset.options, input);
      if (passwordInput) passwordInput.value = '';
      const options = result.publicKey;
      options.challenge = decode(options.challenge);
      if (options.user) options.user.id = decode(options.user.id);
      for (const key of ['allowCredentials', 'excludeCredentials']) {
        if (options[key]) options[key] = options[key].map((item) => ({ ...item, id: decode(item.id) }));
      }
      const credential = purpose === 'register'
        ? await navigator.credentials.create({ publicKey: options })
        : await navigator.credentials.get({ publicKey: options });
      if (!credential) throw new Error('La verificación fue cancelada.');
      const response = { clientDataJSON: encode(credential.response.clientDataJSON) };
      if (purpose === 'register') {
        response.attestationObject = encode(credential.response.attestationObject);
        response.transports = credential.response.getTransports?.() || [];
      } else {
        response.authenticatorData = encode(credential.response.authenticatorData);
        response.signature = encode(credential.response.signature);
        response.userHandle = credential.response.userHandle ? encode(credential.response.userHandle) : null;
      }
      await post(root.dataset.verify, { purpose, challenge_id: result.challenge_id,
        credential: { id: credential.id, rawId: encode(credential.rawId), type: credential.type,
          authenticatorAttachment: credential.authenticatorAttachment,
          clientExtensionResults: credential.getClientExtensionResults(), response } });
      if (purpose === 'register') {
        registered = true;
        document.getElementById('receipt-enroll')?.remove();
        status.textContent = 'Dispositivo registrado. Ya podés firmar el recibo.';
      } else window.location.reload();
    } catch (error) {
      status.textContent = ['NotAllowedError', 'AbortError'].includes(error.name)
        ? 'Verificación cancelada o vencida. El recibo sigue pendiente.' : error.message;
    } finally {
      if (passwordInput) passwordInput.value = '';
      buttons.forEach((button) => { button.disabled = button.hasAttribute('data-sign') && !registered; });
    }
  }
  document.getElementById('receipt-register')?.addEventListener('click', () => ceremony('register'));
  root.querySelectorAll('[data-sign]').forEach((button) => {
    button.addEventListener('click', () => ceremony('sign', button.dataset.sign));
  });
})();
