import { For, Show, createSignal, type JSXElement } from "solid-js";
import "./tabbed-media.css";

export type TabbedMediaTab = {
  id: string;
  label: string;
  media: {
    type: "image" | "video";
    src: string;
    alt?: string;
    poster?: string;
  };
  /** Optional secondary control labels (e.g. people heights). */
  people?: Array<{ id: string; label: string; media?: TabbedMediaTab["media"] }>;
};

export type TabbedMediaProps = {
  eyebrow?: string;
  title: string;
  tabs: TabbedMediaTab[];
  /** Slot for an action button overlaid on media (e.g. View size / specs). */
  renderMediaAction?: () => JSXElement;
  class?: string;
  id?: string;
};

export function TabbedMedia(props: TabbedMediaProps) {
  const [tabId, setTabId] = createSignal(props.tabs[0]?.id ?? "");
  const [personId, setPersonId] = createSignal(props.tabs[0]?.people?.[0]?.id ?? "");
  const [paused, setPaused] = createSignal(false);
  let videoRef: HTMLVideoElement | undefined;

  const activeTab = () => props.tabs.find((t) => t.id === tabId()) ?? props.tabs[0];
  const activeMedia = () => {
    const tab = activeTab();
    const person = tab?.people?.find((p) => p.id === personId());
    return person?.media ?? tab?.media;
  };

  const selectTab = (id: string) => {
    setTabId(id);
    const next = props.tabs.find((t) => t.id === id);
    setPersonId(next?.people?.[0]?.id ?? "");
    setPaused(false);
  };

  const togglePause = () => {
    const el = videoRef;
    if (!el) return;
    if (el.paused) {
      void el.play();
      setPaused(false);
    } else {
      el.pause();
      setPaused(true);
    }
  };

  return (
    <section id={props.id} class={["tm", props.class].filter(Boolean).join(" ")} aria-labelledby={props.id ? `${props.id}-title` : undefined}>
      <div class="tm__header">
        <div class="tm__titles">
          <Show when={props.eyebrow}>
            <p class="tm__eyebrow">{props.eyebrow}</p>
          </Show>
          <h2 class="tm__title" id={props.id ? `${props.id}-title` : undefined}>
            {props.title}
          </h2>
        </div>

        <div class="tm__tabs" role="tablist" aria-label="Product modes">
          <For each={props.tabs}>
            {(tab) => (
              <button
                type="button"
                role="tab"
                class="tm__tab"
                classList={{ "is-active": tabId() === tab.id }}
                aria-selected={tabId() === tab.id}
                onClick={() => selectTab(tab.id)}
              >
                {tab.label}
              </button>
            )}
          </For>
        </div>
      </div>

      <div class="tm__stage" role="tabpanel">
        <Show when={activeMedia()} keyed>
          {(media) => (
            <div class="tm__frame">
              <Show
                when={media.type === "video"}
                fallback={<img class="tm__asset" src={media.src} alt={media.alt ?? ""} />}
              >
                <video
                  ref={videoRef}
                  class="tm__asset"
                  src={media.src}
                  poster={media.poster}
                  muted
                  loop
                  playsinline
                  autoplay
                  aria-label={media.alt ?? "Product demonstration"}
                />
              </Show>

              <div class="tm__controls">
                <Show when={media.type === "video"}>
                  <button type="button" class="tm__chip" onClick={togglePause}>
                    {paused() ? "Play" : "Pause"}
                  </button>
                </Show>
                <Show when={props.renderMediaAction}>{props.renderMediaAction!()}</Show>
              </div>
            </div>
          )}
        </Show>

        <Show when={(activeTab()?.people?.length ?? 0) > 0}>
          <div class="tm__people" role="group" aria-label="Model height">
            <For each={activeTab()!.people!}>
              {(person) => (
                <button
                  type="button"
                  class="tm__person"
                  classList={{ "is-active": personId() === person.id }}
                  aria-pressed={personId() === person.id}
                  onClick={() => setPersonId(person.id)}
                >
                  {person.label}
                </button>
              )}
            </For>
          </div>
        </Show>
      </div>
    </section>
  );
}

export default TabbedMedia;
