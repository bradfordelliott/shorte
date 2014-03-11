#ifndef SCRIPTSYNTAXHIGHLIGHTER_H
#define SCRIPTSYNTAXHIGHLIGHTER_H
#include <QSyntaxHighlighter>
#include <QMap>
#include <QString>


class mySyntaxHighLighter: public QSyntaxHighlighter
{

  public:
    mySyntaxHighLighter(QTextDocument* document):
    QSyntaxHighlighter(document)
    {
    }

    void set_link_words(QMap<QString, QString>& link_words)
    {
        m_link_words = link_words;
    }

    ~ mySyntaxHighLighter()
    {}

    void highlightBlock(const QString &input)
    {
        enum { NormalState = -1, CStyleComment, CStyleString, CStyleQuotes, CStyleWord};
        QString curr_word;
        int curr_word_start = 0;

        int state = previousBlockState();
        int start = 0;
        QColor cmt_color(0x00, 0x99, 0x33);
        QColor define_color(0, 200, 0);
        QColor color_operator(0, 0, 200);

        QString text = input;
        text += "\n";

        for (int i = 0; i < text.length();)
        {
            if (state == CStyleComment)
            {
                if (text.mid(i, 2) == "*/")
                {
                    state = NormalState;
                    setFormat(start, i - start + 2, cmt_color);
                    i += 2;
                }
                else
                {
                    setFormat(start, text.length() - i, cmt_color);
                    i += 1;
                }
            }
            else if (state == CStyleString)
            {
                if(text.mid(i,1) == "\"")
                {
                    state = NormalState;
                    setFormat(start, (i-start)+1, Qt::magenta);
                }
                i += 1;
            }
            else if (state == CStyleQuotes)
            {
                if(text.mid(i,1) == "\'")
                {
                    state = NormalState;
                    setFormat(start, i-start+1, Qt::magenta);
                }

                i += 1;
            }
            else if (state == CStyleWord)
            {
                char curr = text.at(i).toLatin1();
                //QString tmp;
                //tmp.append(curr);

                //QMessageBox::information(NULL, curr_word, tmp);

                if(((curr >= 'a' && curr <= 'z') ||
                    (curr >= 'A' && curr <= 'Z') ||
                    (curr >= '0' && curr <= '9') ||
                    (curr == '_')))
                {
                    curr_word.append(curr);
                    //QMessageBox::information(NULL, curr_word, curr_word);
                    i += 1;
                }
                else
                {
                    //QMessageBox::information(NULL, curr_word, curr_word);

                    if(m_link_words.contains(curr_word))
                    {
                        QTextCharFormat format;
                        format.setAnchor(true);
                        QString anchor = m_link_words[curr_word];
                        format.setAnchorHref(anchor);
                        format.setUnderlineStyle(QTextCharFormat::SingleUnderline);
                            //format.setForeground(QBrush(Qt::blue));
                            //format.setUnderlineColor(Qt::blue);

                        QColor cmt_color(Qt::blue);
                        //QColor cmt_color(0x66, 0x99, 0xff);
                        format.setForeground(QBrush(cmt_color));
                        format.setUnderlineColor(cmt_color);


                        setFormat(curr_word_start, curr_word.length(), format);
                    }

                    curr_word.clear();
                    curr_word_start = 0;
                    i += 1;
                    state = NormalState;
                }
            }
            else
            {
                if (text.mid(i, 2) == "//")
                {
                    setFormat(i, text.length() - i, cmt_color);
                    i += 2;
                    break;
                }
                else if(text.mid(i,1) == "#")
                {
                    setFormat(i, text.length() - i, define_color);
                    i += 1;
                    break;
                }
                else if(text.mid(i,1) == "\"")
                {
                    start = i;
                    state = CStyleString;
                    //setFormat(i, 1, Qt::magenta);
                    i += 1;
                }
                else if(text.mid(i,1) == "\'")
                {
                    start = i;
                    state = CStyleQuotes;
                    setFormat(i, 1, Qt::magenta);
                    i += 1;
                }
                else if (text.mid(i, 2) == "/*")
                {
                    start = i;
                    state = CStyleComment;
                    setFormat(i, text.length() - i, cmt_color);
                    i += 2;
                }
                else
                {
                    char curr = text.at(i).toLatin1();

                    if((curr >= 'a' && curr <= 'z') ||
                       (curr >= 'A' && curr <= 'Z'))
                    {
                        curr_word.clear();
                        curr_word.append(QChar(curr));
                        curr_word_start = i;
                        state = CStyleWord;
                    }

                    i += 1;
                }

            }
        }
        setCurrentBlockState(state);
    };

    private:
        QMap<QString, QString> m_link_words;
};

#endif // SCRIPTSYNTAXHIGHLIGHTER_H
