import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SearchInput } from "../../src/components/SearchInput";

const noop = () => {};

describe("SearchInput", () => {
  describe("hint message", () => {
    it("is hidden when query is empty", () => {
      render(<SearchInput value="" onChange={noop} onRefresh={noop} />);
      expect(screen.queryByText(/keep typing/i)).not.toBeInTheDocument();
    });

    it("is visible when query has 1 char", () => {
      render(<SearchInput value="B" onChange={noop} onRefresh={noop} />);
      expect(screen.getByText(/keep typing/i)).toBeInTheDocument();
    });

    it("is visible when query has 2 chars", () => {
      render(<SearchInput value="Br" onChange={noop} onRefresh={noop} />);
      expect(screen.getByText(/keep typing/i)).toBeInTheDocument();
    });

    it("is hidden when query has 3+ chars", () => {
      render(<SearchInput value="Bru" onChange={noop} onRefresh={noop} />);
      expect(screen.queryByText(/keep typing/i)).not.toBeInTheDocument();
    });
  });

  describe("refresh button", () => {
    it("is disabled when query is shorter than 3 chars", () => {
      render(<SearchInput value="Br" onChange={noop} onRefresh={noop} />);
      expect(screen.getByRole("button", { name: /refresh/i })).toBeDisabled();
    });

    it("is enabled when query has 3+ chars", () => {
      render(<SearchInput value="Bru" onChange={noop} onRefresh={noop} />);
      expect(
        screen.getByRole("button", { name: /refresh/i }),
      ).not.toBeDisabled();
    });
  });
});
