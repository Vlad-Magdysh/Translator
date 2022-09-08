#pragma once

#include <iostream>
#include <vector>
#include <string>
using Message = std::vector<char>; // type alias for std::vector<char>

std::ostream& operator<< (std::ostream& out, const Message& v);

class OutputStrategy
{
public:
	virtual void display_answer(const Message& answer, const size_t answer_size) const = 0;
	virtual ~OutputStrategy() = default;
};

class OutputInFile : public OutputStrategy
{
private:
	std::string m_file_destination;

public:
	OutputInFile(const std::string& dest);
	virtual void display_answer(const Message& answer, const size_t answer_size) const override final;
};

class OutputInStdout : public OutputStrategy
{
public:
	virtual void display_answer(const Message& answer, const size_t answer_size) const override final;
};

class OutputInMessageBox : public OutputStrategy
{
private:
	std::wstring convert_utf8_to_utf_16(const char* message_start, size_t message_size) const;
public:
	virtual void display_answer(const Message& answer, const size_t answer_size) const override final;
};
