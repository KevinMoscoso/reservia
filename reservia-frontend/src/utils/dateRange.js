function defaultDateRange() {
  const today = new Date();
  const fechaFin = today.toISOString().slice(0, 10);
  const start = new Date(today);
  start.setDate(start.getDate() - 30);
  const fechaInicio = start.toISOString().slice(0, 10);
  return { fechaInicio, fechaFin };
}
export { defaultDateRange };