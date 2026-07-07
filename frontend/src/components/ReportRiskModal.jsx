import { useEffect, useState } from "react";
import { HAZARD_CATEGORIES } from "../config/hazardCategories";
import { createRisk } from "../api/client";

const RISK_TYPE_MIN_LENGTH = 3;
const RISK_TYPE_MAX_LENGTH = 500;

export default function ReportRiskModal({ location, onClose, onSubmitted }) {
  const [hazardCategory, setHazardCategory] = useState("");
  const [mainCategory, setMainCategory] = useState("");
  const [riskType, setRiskType] = useState("");
  const [address, setAddress] = useState("");
  const [submitAttempted, setSubmitAttempted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [isSuccess, setIsSuccess] = useState(false);

  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const trimmedMainCategory = mainCategory.trim();
  const trimmedRiskType = riskType.trim();

  const errors = {};
  if (!hazardCategory) {
    errors.hazardCategory = "Wybierz kategorię zagrożenia";
  }
  if (!trimmedMainCategory) {
    errors.mainCategory = "Pole nie może być puste";
  }
  if (trimmedRiskType.length < RISK_TYPE_MIN_LENGTH) {
    errors.riskType = `Opis musi mieć co najmniej ${RISK_TYPE_MIN_LENGTH} znaki`;
  } else if (trimmedRiskType.length > RISK_TYPE_MAX_LENGTH) {
    errors.riskType = `Opis może mieć maksymalnie ${RISK_TYPE_MAX_LENGTH} znaków`;
  }
  const hasErrors = Object.keys(errors).length > 0;

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitAttempted(true);
    if (hasErrors) return;

    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const newRisk = await createRisk({
        main_category: trimmedMainCategory,
        hazard_category: hazardCategory,
        risk_type: trimmedRiskType,
        address: address.trim() || null,
        lat: location.lat,
        lng: location.lng,
      });
      setIsSuccess(true);
      setTimeout(() => {
        onSubmitted(newRisk);
        onClose();
      }, 1400);
    } catch (err) {
      setSubmitError(err.message);
      setIsSubmitting(false);
    }
  }

  return (
    <div className="report-modal-overlay" onClick={onClose}>
      <div
        className="report-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Zgłoś zagrożenie"
      >
        <div className="report-modal-header">
          <h2>Zgłoś zagrożenie</h2>
          <button
            type="button"
            className="report-modal-close"
            onClick={onClose}
            aria-label="Zamknij"
          >
            ×
          </button>
        </div>

        {isSuccess ? (
          <p className="report-modal-success">
            Zgłoszenie zostało przyjęte i oczekuje na weryfikację.
          </p>
        ) : (
          <form
            className="report-modal-form"
            onSubmit={handleSubmit}
            noValidate
          >
            <p className="report-modal-location">
              Wybrana lokalizacja: {location.lat.toFixed(4)},{" "}
              {location.lng.toFixed(4)}
            </p>

            <label className="report-modal-field">
              Kategoria zagrożenia *
              <select
                value={hazardCategory}
                onChange={(e) => setHazardCategory(e.target.value)}
              >
                <option value="">Wybierz kategorię…</option>
                {Object.entries(HAZARD_CATEGORIES).map(([key, { label }]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
              {submitAttempted && errors.hazardCategory && (
                <span className="report-modal-error">
                  {errors.hazardCategory}
                </span>
              )}
            </label>

            <label className="report-modal-field">
              Kategoria obiektu lub miejsca *
              <input
                type="text"
                value={mainCategory}
                onChange={(e) => setMainCategory(e.target.value)}
                placeholder="np. Infrastruktura krytyczna"
              />
              {submitAttempted && errors.mainCategory && (
                <span className="report-modal-error">
                  {errors.mainCategory}
                </span>
              )}
            </label>

            <label className="report-modal-field">
              Opis zagrożenia *
              <textarea
                value={riskType}
                onChange={(e) => setRiskType(e.target.value)}
                rows={4}
                maxLength={RISK_TYPE_MAX_LENGTH}
                placeholder="Opisz zaobserwowane zagrożenie…"
              />
              <span className="report-modal-char-count">
                {trimmedRiskType.length}/{RISK_TYPE_MAX_LENGTH}
              </span>
              {submitAttempted && errors.riskType && (
                <span className="report-modal-error">{errors.riskType}</span>
              )}
            </label>

            <label className="report-modal-field">
              Adres
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="np. ul. Kozielska 52"
              />
            </label>

            {submitError && (
              <p className="report-modal-submit-error">{submitError}</p>
            )}

            <div className="report-modal-actions">
              <button type="button" onClick={onClose} disabled={isSubmitting}>
                Anuluj
              </button>
              <button type="submit" disabled={hasErrors || isSubmitting}>
                {isSubmitting ? "Wysyłanie…" : "Wyślij"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
