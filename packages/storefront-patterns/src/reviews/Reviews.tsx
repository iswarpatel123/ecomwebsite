import { For, Show, createSignal, type JSXElement } from "solid-js";
import "./reviews.css";

export type ReviewItem = {
  id: string;
  author: string;
  initials?: string;
  rating: number;
  title: string;
  body: string;
  verified?: boolean;
  recommends?: boolean;
  helpfulYes?: number;
  helpfulNo?: number;
  imageSrc?: string;
};

export type ReviewsProps = {
  title?: string;
  averageRating: number;
  totalCount: number;
  /** Counts for 5..1 stars. */
  ratingBreakdown: number[];
  recommendPercent?: number;
  reviews: ReviewItem[];
  initiallyVisible?: number;
  class?: string;
  id?: string;
  renderFilters?: () => JSXElement;
};

function stars(n: number) {
  const filled = Math.round(Math.min(5, Math.max(0, n)));
  return "★".repeat(filled) + "☆".repeat(5 - filled);
}

export function Reviews(props: ReviewsProps) {
  const visible = () => props.initiallyVisible ?? 3;
  const [shown, setShown] = createSignal(visible());
  const max = Math.max(...props.ratingBreakdown, 1);
  const list = () => props.reviews.slice(0, shown());

  return (
    <section id={props.id ?? "reviews"} class={["rv", props.class].filter(Boolean).join(" ")} aria-labelledby="rv-title">
      <h2 id="rv-title" class="rv__title">
        {props.title ?? "Customer Reviews"}
      </h2>

      <div class="rv__summary">
        <div class="rv__score-block">
          <div class="rv__score" aria-hidden="true">
            {props.averageRating.toFixed(1)}
          </div>
          <div>
            <div class="rv__stars" aria-label={`Rated ${props.averageRating} out of 5`}>
              {stars(props.averageRating)}
            </div>
            <p class="rv__based">Based on {props.totalCount.toLocaleString()} reviews</p>
          </div>
        </div>

        <ol class="rv__bars" aria-label="Rating breakdown">
          <For each={[5, 4, 3, 2, 1]}>
            {(star, i) => {
              const count = () => props.ratingBreakdown[i()] ?? 0;
              const pct = () => Math.round((count() / max) * 100);
              return (
                <li class="rv__bar-row">
                  <span>{star}</span>
                  <div class="rv__bar" aria-hidden="true">
                    <span style={{ width: `${pct()}%` }} />
                  </div>
                  <span>{formatCount(count())}</span>
                </li>
              );
            }}
          </For>
        </ol>

        <Show when={props.recommendPercent !== undefined}>
          <p class="rv__recommend">
            <strong>{props.recommendPercent}%</strong> would recommend this product
          </p>
        </Show>
      </div>

      <div class="rv__toolbar">
        <Show when={props.renderFilters} fallback={
          <>
            <button type="button" class="rv__btn">Filters</button>
            <button type="button" class="rv__btn">Write a Review</button>
          </>
        }>
          {props.renderFilters!()}
        </Show>
      </div>

      <div class="rv__list-head">
        <span>{props.totalCount.toLocaleString()} reviews</span>
        <label class="rv__sort">
          Sort
          <select>
            <option>Photos &amp; Videos</option>
            <option>Most recent</option>
            <option>Highest rated</option>
          </select>
        </label>
      </div>

      <ul class="rv__list">
        <For each={list()}>
          {(review) => (
            <li class="rv__item">
              <div class="rv__author">
                <span class="rv__avatar" aria-hidden="true">
                  {review.initials ?? initials(review.author)}
                </span>
                <div>
                  <p class="rv__name">{review.author}</p>
                  <Show when={review.verified !== false}>
                    <p class="rv__verified">Verified Buyer <span aria-hidden="true">✓</span></p>
                  </Show>
                  <Show when={review.recommends !== false}>
                    <p class="rv__thumb">👍 I recommend this product</p>
                  </Show>
                </div>
              </div>

              <div class="rv__content">
                <div class="rv__stars" aria-label={`${review.rating} out of 5 stars`}>
                  {stars(review.rating)}
                </div>
                <h3 class="rv__headline">{review.title}</h3>
                <p class="rv__body">{review.body}</p>
                <p class="rv__helpful">
                  Was this helpful?
                  <button type="button" class="rv__vote" aria-label="Mark helpful">👍 {review.helpfulYes ?? 0}</button>
                  <button type="button" class="rv__vote" aria-label="Mark not helpful">👎 {review.helpfulNo ?? 0}</button>
                </p>
              </div>

              <div class="rv__photo" aria-hidden={!review.imageSrc}>
                <Show when={review.imageSrc}>
                  <img src={review.imageSrc} alt="" loading="lazy" />
                </Show>
              </div>
            </li>
          )}
        </For>
      </ul>

      <Show when={shown() < props.reviews.length}>
        <div class="rv__more-wrap">
          <button type="button" class="rv__more" onClick={() => setShown(props.reviews.length)}>
            Show More
          </button>
        </div>
      </Show>
    </section>
  );
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function formatCount(n: number) {
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1).replace(/\.0$/, "")}k`;
  return String(n);
}

export default Reviews;
