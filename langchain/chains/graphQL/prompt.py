

prompt = """Here is the Open Targets GraphQL API schema summary:

The GraphQL API schema of Open Targets consists of four main types: Targets, Diseases, Drugs, and Associations. Targets represent the genes, proteins, and other molecules that are the focus of research, while Diseases are the conditions or disorders that are being studied. Drugs are the substances that are used to treat or prevent a disease. These types are connected in the following way: Targets and Diseases are connected through Associations, and Drugs and Diseases are connected through Associations. 

Each type has several fields that contain data related to the type. For Targets, these fields include the gene name, symbol, NCBI ID, description, and function, as well as information about the gene's location, homology, expression, and pathways. For Diseases, the fields include the disease name and description, as well as the associated ICD-10 codes. For Drugs, the fields include the drug name, dosage, and mechanism of action. Finally, the Associations type contains fields that show the type of association (e.g. therapeutic or toxic), the strength of the association, and the evidence supporting the association. 

The GraphQL API schema also allows users to apply filters and sorting to the data, such as gene or disease name, and offers support for pagination. Additionally, the API supports nested queries, allowing users to query related data in a single request.

Here are the few examples of questions and the corresponding GraphQL query:

Question: What are the top 3 diseases associated with ABCA4?
query search {
  search(queryString: "ABCA4", entityNames: "target") {
   hits { id,
          name, 
          entity,
           object {
              ... on Target {
             associatedDiseases(page: {index: 0, size: 3}) {
                rows {
                 score
                  disease {
                    name
                      }
                 }
             }
         }
     }
  }
}
}

Question: Write a query that returns Genetic Constraint and Tractability data for ensemblId - ENSG00000169083 
query targetInfo {
  target(ensemblId: "ENSG00000169083") {
    id
    approvedSymbol
    biotype
    geneticConstraint{
      constraintType
      exp
      obs
      score
      oe
      oeLower
      oeUpper
    }
    tractability{
      id
      modality
      value
    }
  }
}

Now with the above summary and the examples, given an input question, create a syntactically correct graphQL query to run
"""

