
from langchain import OpenAI
from langchain.chains.graphQL.base import GraphQLChain
from langchain.graphQL import GraphQL


db: GraphQL = GraphQL()

llm: OpenAI = OpenAI(model_name="gpt-3.5-turbo", temperature=0)

db_chain: GraphQLChain = GraphQLChain(llm=llm, database=db, verbose=True)
query = str(input("Hi, You can now talk to open targets database. \n"))
db_chain.run(query)


