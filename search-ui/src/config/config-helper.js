import { MultiCheckboxFacet } from "@elastic/react-search-ui-views";
/**
 * This file abstracts most logic around the configuration of the Reference UI.
 *
 * Configuration is an important part of the "reusability" and "generic-ness" of
 * the Reference UI, but if you are using this app as a starting point for own
 * project, everything related to configuration can largely be thrown away. To
 * that end, this file attempts to contain most of that logic to one place.
 */

function toLowerCase(string) {
  if (string) return string.toLowerCase();
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function getTitleField(config) {
  // If no title field configuration has been provided, we attempt
  // to use a "title" field, if one exists
  return config.titleField || "title";
}

export function getUrlField(config) {
  return config.urlField;
}

export function getThumbnailField(config) {
  return config.thumbnailField;
}

export function getFacetFields(config) {
  return (config.searchQuery.facets && Object.keys(config.searchQuery.facets)) || [];
}

export function getSortFields(config) {
  return config.sortFields || [];
}

export function getResultTitle(result) {
  const titleField = getTitleField();

  return result.getSnippet(titleField);
}

// Because if a field is configured to display as a "title", we don't want
// to display it again in the fields list
export function stripUnnecessaryResultFields(resultFields) {
  return Object.keys(resultFields).reduce((acc, n) => {
    if (
      [
        "_meta",
        "id",
        toLowerCase(getTitleField()),
        toLowerCase(getUrlField()),
        toLowerCase(getThumbnailField()),
      ].includes(toLowerCase(n))
    ) {
      return acc;
    }

    acc[n] = resultFields[n];
    return acc;
  }, {});
}

// export function buildSearchOptionsFromConfig(config) {
//   const searchFields = (config.searchFields || config.fields || []).reduce(
//     (acc, n) => {
//       acc = acc || {};
//       acc[n] = {};
//       return acc;
//     },
//     undefined
//   );

//   const resultFields = (config.resultFields || config.fields || []).reduce(
//     (acc, n) => {
//       acc = acc || {};
//       acc[n] = {
//         raw: {},
//         snippet: {
//           size: 100,
//           fallback: true
//         }
//       };
//       return acc;
//     },
//     undefined
//   );

//   // We can't use url, thumbnail, or title fields unless they're actually
//   // in the reuslts.
//   if (config.urlField) {
//     resultFields[config.urlField] = {
//       raw: {},
//       snippet: {
//         size: 100,
//         fallback: true
//       }
//     };
//   }

//   if (config.thumbnailField) {
//     resultFields[config.thumbnailField] = {
//       raw: {},
//       snippet: {
//         size: 100,
//         fallback: true
//       }
//     };
//   }

//   if (config.titleField) {
//     resultFields[config.titleField] = {
//       raw: {},
//       snippet: {
//         size: 100,
//         fallback: true
//       }
//     };
//   }

//   const searchOptions = {};
//   searchOptions.result_fields = resultFields;
//   searchOptions.search_fields = searchFields;
//   return searchOptions;
// }

export function buildFacetConfigFromConfig(config) {
  const facets = config.searchQuery.facets || {};
  const result = [];

  for (const field in facets) {
    const facetConfig = facets[field];
    const label = field
      .replace(/\.keyword$/, "")
      .replace(/\.as_float$/, "")
      .replace(/_/g, " "); // optional: make it more human-friendly

    const view = facetConfig.view || MultiCheckboxFacet;

    result.push({ field, label, view });
  }
  
  return result;
}

export function buildSortOptionsFromConfig(config) {
  return [
    {
      name: "Relevance",
      value: "",
      direction: ""
    },
    ...(config.sortFields || []).reduce((acc, sortField) => {
      const {field, value} = sortField;
      acc.push({
        name: `${capitalizeFirstLetter(field)} ASC`,
        value: value,
        direction: "asc"
      });
      acc.push({
        name: `${capitalizeFirstLetter(field)} DESC`,
        value: value,
        direction: "desc"
      });
      return acc;
    }, [])
  ];
}

// export function buildAutocompleteQueryConfig(config) {
//   const querySuggestFields = config.querySuggestFields;
//   if (
//     !querySuggestFields ||
//     !Array.isArray(querySuggestFields) ||
//     querySuggestFields.length === 0
//   ) {
//     return {};
//   }

//   return {
//     suggestions: {
//       types: {
//         documents: {
//           fields: buildSortOptionsFromConfig.querySuggestFields
//         }
//       }
//     }
//   };
// }
