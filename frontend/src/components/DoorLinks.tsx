import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  showSearch?: boolean;
  showPublish?: boolean;
  onSearchHome?: () => void;
  onSearchWork?: () => void;
  onPublish?: () => void;
};

/** Quiet links: back to housing/job search, or to publish. */
export function DoorLinks({
  t,
  showSearch = false,
  showPublish = true,
  onSearchHome,
  onSearchWork,
  onPublish,
}: Props) {
  if (!showSearch && !showPublish) {
    return null;
  }
  return (
    <nav className="door-links">
      {showSearch && onSearchHome ? (
        <button type="button" className="post-ad-link" onClick={onSearchHome}>
          {t.searchHomeCta}
        </button>
      ) : null}
      {showSearch && onSearchWork ? (
        <button type="button" className="post-ad-link" onClick={onSearchWork}>
          {t.searchWorkCta}
        </button>
      ) : null}
      {showPublish && onPublish ? (
        <button type="button" className="post-ad-link" onClick={onPublish}>
          {t.postAdCta}
        </button>
      ) : null}
    </nav>
  );
}
