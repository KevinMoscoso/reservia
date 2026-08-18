import { apiFetch } from './client';

function getOccupancyReport(fechaInicio, fechaFin) {
  return apiFetch(`/reports/occupancy?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`);
}
function getProviderActivityReport(fechaInicio, fechaFin) {
  return apiFetch(`/reports/providers?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`);
}
function getSystemActivityReport(fechaInicio, fechaFin) {
  return apiFetch(`/reports/system?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`);
}
async function downloadReportCsv(path, fechaInicio, fechaFin, filename) {
  const response = await fetch(
    `/api${path}?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&format=csv`,
    { credentials: 'include' }
  );
  if (!response.ok) {
    throw new Error('No se pudo exportar el reporte.');
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export { getOccupancyReport, getProviderActivityReport, getSystemActivityReport, downloadReportCsv };