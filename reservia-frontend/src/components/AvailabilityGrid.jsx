function AvailabilityGrid({ blocks, selectedStart, onSelect }) {
  return (
    <div className="grid grid-cols-4 gap-2 sm:grid-cols-6">
      {blocks.map((block) => {
        const isSelected = block.hora_inicio === selectedStart;

        let className = 'rounded px-3 py-2 text-sm';
        if (!block.disponible) {
          className += ' bg-gray-200 text-gray-400 cursor-not-allowed';
        } else if (isSelected) {
          className += ' bg-blue-600 text-white';
        } else {
          className += ' bg-green-100 hover:bg-green-200';
        }

        return (
          <button
            key={block.hora_inicio}
            type="button"
            disabled={!block.disponible}
            onClick={() => onSelect(block.hora_inicio)}
            className={className}
          >
            {block.hora_inicio.slice(0, 5)}
          </button>
        );
      })}
    </div>
  );
}

export default AvailabilityGrid;