(function (root) {
  'use strict';

  const DEFAULT_ENDPOINT = '';

  async function checked(response) {
    if (!response.ok) {
      const text = await response.text();
      const error = new Error(text || `HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    }
    return response;
  }

  async function uploadFile(file, endpoint, headers) {
    const body = new FormData();
    body.append('files', file, file.name);
    const response = await checked(await fetch(`${endpoint}/gradio_api/upload`, {
      method: 'POST', body, headers,
    }));
    const paths = await response.json();
    return { path: paths[0], orig_name: file.name, meta: { _type: 'gradio.FileData' } };
  }

  async function submit(fileData, options, endpoint, headers) {
    const response = await checked(await fetch(`${endpoint}/gradio_api/call/enhance`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify({ data: [fileData, JSON.stringify(options)] }),
    }));
    return (await response.json()).event_id;
  }

  async function collect(eventId, endpoint, headers) {
    const response = await checked(await fetch(
      `${endpoint}/gradio_api/call/enhance/${eventId}`, { headers },
    ));
    const text = await response.text();
    const complete = text.split('\n').filter(line => line.startsWith('data: ')).pop();
    if (!complete) throw new Error('웹 AI 응답을 읽을 수 없습니다.');
    const data = JSON.parse(complete.slice(6));
    if (!Array.isArray(data) || data.length < 2) throw new Error('웹 AI 결과 형식이 올바르지 않습니다.');
    return data;
  }

  async function requestEnhancement(file, options, endpoint = DEFAULT_ENDPOINT, token = '') {
    if (!endpoint) throw new Error('Colab 서버 주소를 먼저 연결해 주세요.');
    const normalized = endpoint.replace(/\/$/, '');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const fileData = await uploadFile(file, normalized, headers);
    const eventId = await submit(fileData, options, normalized, headers);
    const [result, metadataText] = await collect(eventId, normalized, headers);
    const metadata = typeof metadataText === 'string' ? JSON.parse(metadataText) : metadataText;
    if (metadata.status !== 'complete') {
      const error = new Error(metadata.message || '웹 AI 처리가 완료되지 않았습니다.');
      error.code = metadata.status;
      throw error;
    }
    const resultUrl = result.url || `${normalized}/gradio_api/file=${encodeURIComponent(result.path)}`;
    const blob = await (await checked(await fetch(resultUrl, { headers }))).blob();
    return { blob, metadata };
  }

  root.FreePhotoAPI = { DEFAULT_ENDPOINT, requestEnhancement };
})(globalThis);
