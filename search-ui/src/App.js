import React from "react";

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

import {
  ErrorBoundary,
  Facet,
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch
} from "@elastic/react-search-ui";
import { Layout, SingleLinksFacet} from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

import {
  buildSortOptionsFromConfig,
  buildFacetConfigFromConfig,
} from "./config/config-helper";

const host = process.env.REACT_APP_ES_HOST || "http://localhost:9200";
const index = process.env.REACT_APP_ES_INDEX || "cv-transcriptions";
console.log(host, index);
const connector = new ElasticsearchAPIConnector({
  host: host,
  index: index
});

const config = {
  searchQuery: {
    search_fields: {
      "generated_text": {}
      , "duration": {} //This does not work
      , "age": {}
      , "gender": {}
      , "accent": {}
    }
    , result_fields: {
      "generated_text": {
        "snippet": { // Highlight the matched terms on the field
          "size": 100
          , "fallback": true
        }
      }
      , "duration": {
        "snippet": {
          "size": 100
          , "fallback": true
        }
      }
      , "age": {
        "snippet": {
          "size": 100
          , "fallback": true
        }
      }
      , "gender": {
        "snippet": {
          "size": 100
          , "fallback": true
        }
      }
      , "accent": {
        "snippet": {
          "size": 100
          , "fallback": true
        }
      }
    }
    , disjunctiveFacets: ["accent.keyword", "gender.keyword", "age.keyword", "generated_text.keyword"]
    , disjunctiveFacetsAnalyticsTags: ["ignore"]
    , facets: {
      "accent.keyword": { type: "value" }
      , "gender.keyword": { type: "value"}
      , "age.keyword": { type: "value"}
      , "generated_text.keyword": { type: "value" }
      , "duration.as_float": {
        type: "range",
        ranges: [
          { from: 0.0, to: 2.0, name: "Less than 2 sec" },
          { from: 2.0, to: 4.0, name: "2-4 sec" },
          { from: 4.0, to: 6.0, name: "4-6 sec" },
          { from: 6.0, to: 10.0, name: "6-10 sec" },
          { from: 10.0, name: "More than 10 sec" }
        ]
        , "view": SingleLinksFacet
      }
    }
  }
  , apiConnector: connector
  , alwaysSearchOnInitialLoad: true
  , sortFields: [
    {
      field: "accent"
      , value: "accent.keyword"
    }
    , {
      field: "gender"
      , value: "gender.keyword"
    }, { 
      field:"age"
      , value: "age.keyword"
    }, {
      field: "generated_text"
      , value: "generated_text.keyword"
    }, {
      field: "duration"
      , value: "duration.as_float"
    }
  ]
  , titleField: "id"
  , autocompleteQuery: {
    results: {
      resultsPerPage: 5
      , search_fields: {
        "generated_text": {}
        , "duration": {}
        , "age": {}
        , "gender": {}
        , "accent": {}
      }
      , result_fields: {
        "generated_text": {
          snippet: {
            size: 100,
            fallback: true
          }
        }
        , "age": {
          snippet: {
            size: 100,
            fallback: true
          }
        }
        , "gender": {
          snippet: {
            size: 100,
            fallback: true
          }
        }
        , "accent": {
          snippet: {
            size: 100,
            fallback: true
          }
        }
        , "duration": {
          snippet: {
            size: 100,
            fallback: true
          }
        }
      }
    } 
  }
  , autocompleteResults: {
    linkTarget: "_blank",
    sectionTitle: "Results",
    titleField: "generated_text", // This will show the 'generated_text' field as the title in autocomplete
    urlField: "url", // Optional: If you have a URL field to link to
    shouldTrackClickThrough: true,
  }
};

// Unable to hide after clicking probably need to rewrite the whole search view
// const CustomAutocompleteResults = ({ results, onClick, config, useAutocomplete }) => { 
//   if (!useAutocomplete) return null;
//   const searchFields = Object.keys(config?.autocompleteQuery?.results?.search_fields || {});
  
//   return (
//     <div role="listbox" className="sui-search-box__autocomplete-container">
//       <div className="sui-search-box__section-title">Results</div>
//       <ul className="sui-search-box__results-list">
//         {results.map((result, i) => (
//           <li key={i} onClick={() => onClick(result)}>
//             {searchFields.map((field) => {
//               const value =
//                 result[field]?.snippet || result[field]?.raw || "N/A";

//               return (
//                 <div key={field}>
//                   <span style={{ fontWeight: "bold" }}>{field}: </span>
//                     <span
//                       className="sui-result__value"
//                       dangerouslySetInnerHTML={{ __html: value }}
//                     />
//                 </div>
//               );
//             })}
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// };

export default function App() {
  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ wasSearched, setSearchTerm }) => ({ wasSearched, setSearchTerm })}>
        {({ wasSearched, setSearchTerm }) => {
          return (
            <div className="App">
              <ErrorBoundary>
                <Layout
                  header={<SearchBox autocompleteSuggestions={false} 
                                    autocompleteMinimumCharacters={3}
                                    autocompleteResults={config.autocompleteResults}
                                    debounceLength={300}
                                    searchAsYouType={true} 
                                    onSelect={(selectedResult) => {
                                      console.log(selectedResult);
                                      if (!selectedResult || !selectedResult.generated_text?.raw) {
                                        // You might want to clear the search box or just return
                                        setSearchTerm(""); // Or maybe do nothing
                                        return;
                                      }
                                      // Example: you can update the search box or trigger a search
                                      setSearchTerm(selectedResult?.generated_text?.raw);
                                    }}
                                    // autocompleteView={({ autocompletedResults, useAutocomplete }) => (
                                    //   <CustomAutocompleteResults results={autocompletedResults} 
                                    //   config={config} 
                                    //   useAutocomplete={useAutocomplete}
                                    //   onClick={(selectedResult) => {
                                    //     setSearchTerm(selectedResult.generated_text.raw);
                                    //     console.log(document.querySelector('.sui-layout-body'));
                                    //   }}/>
                                    // )}
                                    />}
                  sideContent={
                    <div>
                      {wasSearched && (
                        <Sorting
                          label={"Sort by"}
                          sortOptions={buildSortOptionsFromConfig(config)}
                        />
                      )}
                      { buildFacetConfigFromConfig(config).map(
                        (info) => {
                          const {field, label, view } = info;
                          return <Facet key={field} field={field} label={label} filterType="any" view={view}/>;
                        }
                      )}
                    </div>
                  }
                  bodyContent={
                    <div>
                    <Results
                    titleField={config.titleField}
                    // urlField={getConfig().urlField}
                    // thumbnailField={getConfig().thumbnailField}
                    shouldTrackClickThrough={true}
                  /></div>
                    
                  }
                  bodyHeader={
                    <React.Fragment>
                      {wasSearched && <PagingInfo />}
                      {wasSearched && <ResultsPerPage />}
                    </React.Fragment>
                  }
                  bodyFooter={<Paging />}
                />
              </ErrorBoundary>
            </div>
          );
        }}
      </WithSearch>
    </SearchProvider>
  );
}
