import { apiFetch } from './client';

function getAuditLog(fechaInicio, fechaFin, page, pageSize) {
  return apiFetch(
    `/audit/?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&page=${page}&page_size=${pageSize}`
  );
}
export { getAuditLog };