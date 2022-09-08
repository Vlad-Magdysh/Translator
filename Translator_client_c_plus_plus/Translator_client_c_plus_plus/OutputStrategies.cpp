#include "OutputStrategies.h"
#include <fstream>
#include <codecvt>
#include <windows.h>

std::ostream& operator<< (std::ostream& out, const Message& v) {
	auto iter = v.begin();
	while (iter != v.end() && *iter != 0)
	{
		out << *iter++;
	}
	return out;
}

OutputInFile::OutputInFile(const std::string& dest) : m_file_destination(dest) {}
void OutputInFile::display_answer(const Message& answer, const size_t answer_size) const {
	std::ofstream fs(m_file_destination, std::ios::app);
	if (!fs)
	{
		std::cerr << "Cannot open the output file." << std::endl;
	}
	else
	{
		fs << answer << "\n";
	}
}

void OutputInStdout::display_answer(const Message& answer, const size_t answer_size) const {
	std::cout << "RESULT: " << answer << "\n";
}

std::wstring OutputInMessageBox::convert_utf8_to_utf_16(const char* message_start, size_t message_size) const {
	std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> converter;
	return converter.from_bytes(message_start, message_start + message_size);
}

void OutputInMessageBox::display_answer(const Message& answer, const size_t answer_size) const {
	const std::wstring wstr = convert_utf8_to_utf_16(answer.data(), answer_size);
	MessageBoxW(HWND_DESKTOP, wstr.c_str(), L"", MB_OK | MB_ICONQUESTION);
}
