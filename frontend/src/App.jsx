import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Upload from "./pages/Upload";
import TopicLearning from "./pages/TopicLearning";
import LessonSetup from "./pages/LessonSetup";
import TeachingRoom from "./pages/TeachingRoom";
import Assessment from "./pages/Assessment";
import Progress from "./pages/Progress";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/topics/:topicId" element={<TopicLearning />} />
        <Route path="/lesson/setup" element={<LessonSetup />} />
        <Route path="/teaching-room/:lessonId" element={<TeachingRoom />} />
        <Route path="/assessment/:lessonId" element={<Assessment />} />
        <Route path="/progress" element={<Progress />} />

        <Route path="/home" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;