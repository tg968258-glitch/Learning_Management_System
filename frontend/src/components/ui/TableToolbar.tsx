"use client";

import { useState } from "react";
import { Filter, RotateCcw, Search, X } from "lucide-react";

type FilterOption = {
  label: string;
  value: string;
};

type FilterConfig = {
  label: string;
  value: string;
  options: FilterOption[];
  onChange: (value: string) => void;
};

export function TableToolbar({
  placeholder,
  value = "",
  onChange,
  filters = [],
}: {
  placeholder: string;
  value?: string;
  onChange?: (value: string) => void;
  filters?: FilterConfig[];
}) {
  const [showFilters, setShowFilters] = useState(false);
  const activeFilterCount = filters.filter((filter) => filter.value !== "all").length;

  const clearFilters = () => {
    filters.forEach((filter) => filter.onChange("all"));
  };

  return (
    <div className="border-b border-(--border) p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex max-w-md flex-1 items-center gap-2 rounded-xl border border-(--border) bg-white px-3 py-2.5">
          <Search
            size={16}
            className="text-slate-400"
          />

          <input
            className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
            placeholder={placeholder}
            value={onChange ? value : undefined}
            onChange={(event) => onChange?.(event.target.value)}
          />

          {value && onChange && (
            <button
              type="button"
              onClick={() => onChange("")}
              className="text-slate-400 transition hover:text-slate-700"
              aria-label="Clear search"
            >
              <X size={15} />
            </button>
          )}
        </div>

        {filters.length > 0 && (
          <button
            type="button"
            className="secondary-button"
            onClick={() => setShowFilters((current) => !current)}
            aria-expanded={showFilters}
          >
            <Filter size={16} />
            Filter
            {activeFilterCount > 0 && (
              <span className="grid h-5 min-w-5 place-items-center rounded-full bg-(--brand) px-1.5 text-[10px] font-bold text-white">
                {activeFilterCount}
              </span>
            )}
          </button>
        )}
      </div>

      {showFilters && filters.length > 0 && (
        <div className="mt-4 flex flex-col gap-3 rounded-2xl border border-(--border) bg-slate-50 p-4 sm:flex-row sm:flex-wrap sm:items-end">
          {filters.map((filter) => (
            <label
              key={filter.label}
              className="min-w-44 flex-1"
            >
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                {filter.label}
              </span>

              <select
                value={filter.value}
                onChange={(event) => filter.onChange(event.target.value)}
                className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
              >
                {filter.options.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          ))}

          {activeFilterCount > 0 && (
            <button
              type="button"
              onClick={clearFilters}
              className="secondary-button"
            >
              <RotateCcw size={15} />
              Clear filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
