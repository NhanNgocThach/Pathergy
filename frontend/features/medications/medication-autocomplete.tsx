"use client";

import { useQuery } from "@tanstack/react-query";
import * as React from "react";

import { Input } from "@/components/ui/input";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { medicationService } from "@/services/health-service";
import type { MedicationSuggestion } from "@/types/health";

const DEBOUNCE_MS = 350;
const MINIMUM_QUERY_LENGTH = 2;

type MedicationAutocompleteProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  onBlur: () => void;
  inputRef: React.Ref<HTMLInputElement>;
  describedBy?: string;
  invalid?: boolean;
};

export function MedicationAutocomplete({
  id,
  value,
  onChange,
  onBlur,
  inputRef,
  describedBy,
  invalid = false,
}: MedicationAutocompleteProps) {
  const { t } = useI18n();
  const [debouncedQuery, setDebouncedQuery] = React.useState("");
  const [isOpen, setIsOpen] = React.useState(false);
  const [activeIndex, setActiveIndex] = React.useState(-1);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const listboxId = `${id}-suggestions`;

  React.useEffect(() => {
    const cleanedQuery = value.trim();
    const nextQuery = cleanedQuery.length >= MINIMUM_QUERY_LENGTH ? cleanedQuery : "";
    const timer = window.setTimeout(() => {
      setDebouncedQuery(nextQuery);
      setIsOpen(Boolean(nextQuery));
      setActiveIndex(-1);
    }, DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [value]);

  React.useEffect(() => {
    function closeOnOutsideClick(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    }
    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
  }, []);

  const query = useQuery({
    queryKey: queryKeys.medicationSuggestions(debouncedQuery),
    queryFn: ({ signal }) => medicationService.suggestions(debouncedQuery, signal),
    enabled: debouncedQuery.length >= MINIMUM_QUERY_LENGTH,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const suggestions = query.data?.data.suggestions.slice(0, 8) ?? [];

  function selectSuggestion(suggestion: MedicationSuggestion) {
    onChange(suggestion.name);
    setDebouncedQuery(suggestion.name);
    setIsOpen(false);
    setActiveIndex(-1);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setIsOpen(true);
      setActiveIndex((current) => Math.min(current + 1, suggestions.length - 1));
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      setIsOpen(true);
      setActiveIndex((current) => current <= 0 ? suggestions.length - 1 : current - 1);
      return;
    }
    if (event.key === "Enter" && isOpen && activeIndex >= 0) {
      event.preventDefault();
      selectSuggestion(suggestions[activeIndex]);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setIsOpen(false);
      setActiveIndex(-1);
    }
  }

  const activeOptionId = activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined;

  return <div className="relative" ref={containerRef}>
    <Input
      id={id}
      ref={inputRef}
      value={value}
      onChange={(event) => {
        onChange(event.target.value);
        setIsOpen(false);
        setActiveIndex(-1);
      }}
      onBlur={onBlur}
      onFocus={() => {
        if (debouncedQuery.length >= MINIMUM_QUERY_LENGTH) setIsOpen(true);
      }}
      onClick={() => {
        if (debouncedQuery.length >= MINIMUM_QUERY_LENGTH) setIsOpen(true);
      }}
      onKeyDown={handleKeyDown}
      autoComplete="off"
      role="combobox"
      aria-autocomplete="list"
      aria-expanded={isOpen}
      aria-controls={listboxId}
      aria-activedescendant={activeOptionId}
      aria-describedby={describedBy}
      aria-invalid={invalid}
    />

    {isOpen ? <div id={listboxId} role="listbox" aria-label={t("medication.suggestions")} className="absolute z-30 mt-1 max-h-72 w-full overflow-y-auto rounded-md border bg-card p-1 shadow-lg">
      {query.isFetching ? <p className="px-3 py-3 text-sm text-muted-foreground" role="status">{t("medication.loadingSuggestions")}</p> : null}
      {!query.isFetching && query.isSuccess && suggestions.length === 0 ? <p className="px-3 py-3 text-sm text-muted-foreground">{t("medication.noSuggestions")}</p> : null}
      {!query.isFetching && query.error ? <p className="px-3 py-3 text-sm text-muted-foreground" role="status">{t("medication.suggestionsUnavailable")}</p> : null}
      {!query.isFetching ? suggestions.map((suggestion, index) => <button
        id={`${listboxId}-option-${index}`}
        key={suggestion.rxcui}
        type="button"
        role="option"
        aria-label={`${suggestion.name}, RxCUI ${suggestion.rxcui}`}
        aria-selected={index === activeIndex}
        className="flex w-full items-center justify-between gap-3 rounded-sm px-3 py-2 text-left text-sm hover:bg-muted aria-selected:bg-muted"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => selectSuggestion(suggestion)}
      >
        <span>{suggestion.name}</span>
        <span className="shrink-0 text-xs text-muted-foreground">RxCUI {suggestion.rxcui}</span>
      </button>) : null}
    </div> : null}
  </div>;
}
