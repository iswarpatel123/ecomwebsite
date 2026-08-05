import { CollectionGrid } from "@repo/storefront-patterns";
import { collectionItems, collectionTitle } from "../../../data/collection.js";
import "./collection-section.css";

export function CollectionSection() {
  return (
    <div class="collection-section">
      <CollectionGrid title={collectionTitle} items={collectionItems} />
    </div>
  );
}

export default CollectionSection;
