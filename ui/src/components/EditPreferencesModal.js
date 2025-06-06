// src/components/EditPreferencesModal.js

import React from "react";
import AsyncSelect from "react-select/async";
import { fetchCitySuggestions, fetchRoleSuggestions } from "../utils/api";

export default function EditPreferencesModal({
  preferredRoles,
  setPreferredRoles,
  preferredCities,
  setPreferredCities,
  employmentTypes,
  setEmploymentTypes,
  onSave,
  onClose,
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 shadow-lg w-full max-w-lg relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-2xl">
          ×
        </button>
        <h2 className="text-xl font-bold mb-4">Edit Your Job Preferences</h2>
        <div className="mb-4">
          <label className="block text-sm mb-1">Preferred Roles</label>
          <AsyncSelect
            isMulti
            cacheOptions
            defaultOptions
            loadOptions={fetchRoleSuggestions}
            value={preferredRoles}
            onChange={setPreferredRoles}
            placeholder="Search & select job roles"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm mb-1">Preferred Cities</label>
          <AsyncSelect
            isMulti
            cacheOptions
            defaultOptions
            loadOptions={fetchCitySuggestions}
            value={preferredCities}
            onChange={setPreferredCities}
            placeholder="Search & select cities"
          />
        </div>
        <div className="mb-4 flex gap-3">
          {["Remote", "Hybrid", "Onsite"].map((type) => (
            <button
              key={type}
              className={`px-4 py-2 rounded-full border text-sm ${
                employmentTypes.includes(type)
                  ? "bg-purple-100 text-purple-600 border-purple-600"
                  : "text-gray-600 border-gray-300"
              }`}
              onClick={() =>
                setEmploymentTypes((prev) =>
                  prev.includes(type)
                    ? prev.filter((t) => t !== type)
                    : [...prev, type]
                )
              }
            >
              {type}
            </button>
          ))}
        </div>
        <button
          onClick={onSave}
          className="bg-purple-600 text-white px-6 py-2 rounded w-full mt-2"
        >
          Save Preferences
        </button>
      </div>
    </div>
  );
}
