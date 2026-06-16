import { useState } from "react";
import TabNavigation from "./components/tabs/TabNavigation";
import { TAB_IDS } from "./config/appConfig";
import AppLayout from "./layout/AppLayout";
import ContentWrapper from "./layout/ContentWrapper";
import DecodeView from "./views/DecodeView";
import EncodeView from "./views/EncodeView";

import { UI_TEXT } from "./i18n";

const TABS = [
  {
    id: TAB_IDS.ENCODE,
    label: UI_TEXT.tabs.encode,
  },
  {
    id: TAB_IDS.DECODE,
    label: UI_TEXT.tabs.decode,
  },
];

function App() {
  const [activeTab, setActiveTab] = useState(TAB_IDS.ENCODE);

  return (
    <AppLayout
      title={UI_TEXT.app.title}
      subtitle={UI_TEXT.app.subtitle}
      badge={UI_TEXT.app.badge}
    >
      <TabNavigation
        tabs={TABS}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <ContentWrapper>
        {activeTab === TAB_IDS.ENCODE ? <EncodeView /> : <DecodeView />}
      </ContentWrapper>
    </AppLayout>
  );
}

export default App;
