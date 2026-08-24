import { useEffect, useState } from 'react';
import { getUnreadCount, listMyNotifications, markAllAsRead, markAsRead } from '../api/notifications';

function formatDate(isoString) {
  return new Date(isoString).toLocaleString();
}

function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    getUnreadCount().then((data) => setUnreadCount(data.count));

    const interval = setInterval(() => {
      getUnreadCount().then((data) => setUnreadCount(data.count));
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  function handleToggle() {
    const nextIsOpen = !isOpen;
    setIsOpen(nextIsOpen);
    if (nextIsOpen) {
      listMyNotifications().then((data) => setNotifications(data.items));
    }
  }

  async function handleMarkAsRead(id) {
    await markAsRead(id);
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, leida: true } : n)));
    setUnreadCount((prev) => Math.max(0, prev - 1));
  }

  async function handleMarkAllAsRead() {
    await markAllAsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })));
    setUnreadCount(0);
  }

  return (
    <div className="relative">
      <button
        onClick={handleToggle}
        className="relative rounded px-2 py-1 text-lg"
        aria-label="Notificaciones"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-xs text-white">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 z-10 mt-2 w-80 rounded border border-gray-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-gray-200 p-2">
            <span className="text-sm font-semibold text-gray-800">Notificaciones</span>
            <button onClick={handleMarkAllAsRead} className="text-xs text-blue-600 hover:underline">
              Marcar todas como leídas
            </button>
          </div>

          {notifications.length === 0 ? (
            <p className="p-3 text-sm text-gray-600">No tienes notificaciones.</p>
          ) : (
            <ul className="max-h-80 overflow-y-auto">
              {notifications.map((notif) => (
                <li
                  key={notif.id}
                  onClick={() => !notif.leida && handleMarkAsRead(notif.id)}
                  className={`cursor-pointer border-b border-gray-100 p-2 text-sm ${
                    notif.leida ? 'bg-white text-gray-500' : 'bg-blue-50 text-gray-800'
                  }`}
                >
                  <p>{notif.mensaje}</p>
                  <p className="text-xs text-gray-400">{formatDate(notif.created_at)}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default NotificationBell;