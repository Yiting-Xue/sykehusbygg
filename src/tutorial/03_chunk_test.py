from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# Example from Norwegian law
example_text = """
A. Om statsforma

0    Overskrifta endra med grunnlovsvedtak 21 mai 2012 kunngjort med res. 15 juni 2012 nr. 522, 6 mai 2014 kunngjort med res. 9 mai 2014 nr. 613.

§ 1.
Kongeriket Noreg er eit fritt, sjølvstendig, udeleleg og uavhendeleg rike. Regjeringsforma er avgrensa og arveleg monarkisk.

§ 2.
Verdigrunnlaget skal framleis vere den kristne og humanistiske arven vår. Denne grunnlova skal tryggje demokratiet, rettsstaten og menneskerettane.

B. Om den utøvande makta, om kongen og den kongelege familien og om religionen

§ 3.
Den utøvande makta er hos kongen, eller hos dronninga dersom ho har fått krona etter reglane i § 6, § 7 eller § 48 i denne grunnlova.

§ 4.
Kongen skal alltid vedkjenne seg den evangelisk-lutherske religionen.

§ 5.
Kongen personleg kan ikkje lastast eller skuldast for noko. Ansvaret ligg på rådet hans.

§ 6.
Arvefølgja er lineal. Berre barn av dronning eller konge, eller av nokon som sjølv har arverett, kan arve, og barnet må vere født i lovleg ekteskap.

§ 7.
Finst det ingen prinsesser eller prinsar med arverett, kan kongen gjere framlegg om etterfølgjar for Stortinget.

§ 8.
Myndig alder for kongen blir fastsett i lov.

§ 9.
Så snart kongen, som myndig, tek til med regjeringa, gjer han denne eiden for Stortinget.

§ 10.
(Oppheva med grunnlovsvedtak 14 mars 1908.)
"""

# Token counter
enc = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
token_count = count_tokens(example_text)

if token_count <= 400:
    all_chunks = [example_text]
else:
    all_chunks = splitter.split_text(example_text)

# print first 10 chunks
for i, chunk in enumerate(all_chunks[:10]):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk)
    print(f"Token count: {count_tokens(chunk)}")


# writ it into a function and test different combinations

def split_text_with_params(text, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    token_count = count_tokens(text)

    if token_count <= chunk_size:
        chunks = [text]
    else:
        chunks = splitter.split_text(text)

    token_counts = [count_tokens(c) for c in chunks]
    avg_tokens = sum(token_counts) / len(token_counts)

    print(f"\n=== chunk_size={chunk_size}, overlap={chunk_overlap} ===")
    print(f"Total chunks: {len(chunks)}")
    print(f"Average tokens per chunk: {avg_tokens:.2f}")
    #print(f"Sample chunk:\n{chunks[0]}")
    print(f"Token count: {token_counts[0]}")

    """ for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk)
        print(f"Token count: {token_counts[i]}") """


split_text_with_params(example_text, chunk_size=400, chunk_overlap=40)
split_text_with_params(example_text, chunk_size=300, chunk_overlap=30)
split_text_with_params(example_text, chunk_size=500, chunk_overlap=50)
split_text_with_params(example_text, chunk_size=600, chunk_overlap=60)
split_text_with_params(example_text, chunk_size=250, chunk_overlap=25)
